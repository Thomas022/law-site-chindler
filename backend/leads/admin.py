import csv

from django import forms
from django.contrib import admin, messages
from django.contrib.admin.models import DELETION, LogEntry
from django.contrib.auth import get_user_model
from django.db.models import Count, Prefetch, Q
from django.http import HttpResponse
from django.http.request import QueryDict
from django.urls import reverse
from django.utils import timezone
from django.utils.html import format_html, format_html_join

from properties.roles import ADMINISTRATOR_GROUP

from .models import Lead, LeadInteraction, LeadTask
from .services import anonymize_lead


class LeadAdminForm(forms.ModelForm):
    class Meta:
        model = Lead
        fields = "__all__"


class NextActionFilter(admin.SimpleListFilter):
    title = "próxima ação"
    parameter_name = "next_action"

    def lookups(self, request, model_admin):
        return (
            ("overdue", "Atrasadas"),
            ("today", "Hoje"),
            ("upcoming", "Futuras"),
            ("none", "Sem próxima ação"),
        )

    def queryset(self, request, queryset):
        now = timezone.now()
        today_end = now.replace(hour=23, minute=59, second=59, microsecond=999999)
        pending = Q(tasks__status=LeadTask.Status.PENDING)
        if self.value() == "overdue":
            return queryset.filter(pending, tasks__due_at__lt=now).distinct()
        if self.value() == "today":
            return queryset.filter(
                pending, tasks__due_at__gte=now, tasks__due_at__lte=today_end
            ).distinct()
        if self.value() == "upcoming":
            return queryset.filter(pending, tasks__due_at__gt=today_end).distinct()
        if self.value() == "none":
            return queryset.exclude(pending).distinct()
        return queryset


class LeadInteractionInline(admin.StackedInline):
    model = LeadInteraction
    extra = 1
    fields = ("kind", "description", "outcome", "occurred_at", "created_by")
    readonly_fields = ("created_by",)
    verbose_name = "Registrar interação"
    verbose_name_plural = "Interações e histórico"
    classes = ("collapse",)

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


class LeadTaskInline(admin.TabularInline):
    model = LeadTask
    extra = 1
    fields = ("kind", "due_at", "responsible", "notes", "status", "completed_at")
    readonly_fields = ("completed_at",)
    verbose_name = "próxima ação"
    verbose_name_plural = "Próximas ações e tarefas"
    classes = ("collapse",)


@admin.register(Lead)
class LeadAdmin(admin.ModelAdmin):
    form = LeadAdminForm
    change_list_template = "admin/leads/lead/change_list.html"
    delete_confirmation_template = "admin/leads/lead/delete_confirmation.html"
    list_display = (
        "interested_summary",
        "property_summary",
        "status_summary",
        "responsible_summary",
        "next_action",
        "received_at",
        "row_actions",
    )
    list_filter = (
        "status",
        "priority",
        "source",
        "responsible",
        NextActionFilter,
        "anonymized_at",
        "created_at",
    )
    search_fields = ("name", "email", "phone", "property_title")
    search_help_text = "Pesquise por nome, telefone, e-mail ou imóvel."
    list_select_related = ("property", "responsible")
    list_per_page = 25
    inlines = (LeadTaskInline, LeadInteractionInline)
    readonly_fields = (
        "property",
        "property_title",
        "name",
        "phone",
        "email",
        "message",
        "contact_actions",
        "source",
        "consent_version",
        "consent_at",
        "last_interaction_at",
        "next_action_summary",
        "completed_at",
        "created_at",
        "updated_at",
        "anonymized_at",
    )
    fieldsets = (
        ("Informações do interessado", {"fields": (("name", "phone"), "email", "contact_actions", "message"), "classes": ("collapse",)}),
        ("Imóvel de interesse", {"fields": ("property", "property_title"), "classes": ("collapse",)}),
        (
            "Situação atual",
            {"fields": (("status", "priority"), ("responsible", "source"), "next_action_summary", ("last_interaction_at", "completed_at"))},
        ),
        (
            "Privacidade e controle",
            {"fields": (("consent_version", "consent_at"), ("created_at", "updated_at"), "anonymized_at"), "classes": ("collapse",)},
        ),
    )
    actions = ("export_csv", "anonymize_selected")

    add_fieldsets = (
        (
            "Novo interessado",
            {
                "fields": (
                    "name",
                    "email",
                    "message",
                    "phone",
                    "property",
                    "responsible",
                    "priority",
                ),
                "description": (
                    "Nome, e-mail e mensagem são obrigatórios. Telefone e imóvel "
                    "podem ser informados posteriormente."
                ),
            },
        ),
    )

    class Media:
        css = {"all": ("leads/admin.css",)}

    def get_fieldsets(self, request, obj=None):
        if obj is None:
            return self.add_fieldsets
        return super().get_fieldsets(request, obj)

    def get_readonly_fields(self, request, obj=None):
        if obj is None:
            return (
                "source",
                "status",
                "property_title",
                "consent_version",
                "consent_at",
                "last_interaction_at",
                "completed_at",
                "created_at",
                "updated_at",
                "anonymized_at",
            )
        return super().get_readonly_fields(request, obj)

    def get_queryset(self, request):
        pending_tasks = LeadTask.objects.filter(status=LeadTask.Status.PENDING).order_by("due_at")
        queryset = super().get_queryset(request)
        if "status__exact" not in request.GET:
            queryset = queryset.exclude(status=Lead.Status.DISCARDED)
        return queryset.prefetch_related(
            Prefetch("tasks", queryset=pending_tasks, to_attr="pending_tasks")
        )

    @admin.display(description="Ações rápidas")
    def contact_actions(self, obj):
        if not obj or obj.anonymized_at:
            return "—"
        digits = "".join(character for character in obj.phone if character.isdigit())
        whatsapp_number = digits if digits.startswith("55") else f"55{digits}"
        return format_html(
            '<a class="button" href="tel:{}">Ligar</a> '
            '<a class="button" href="mailto:{}">E-mail</a> '
            '<a class="button" href="https://wa.me/{}" target="_blank" rel="noopener">WhatsApp</a>',
            digits,
            obj.email,
            whatsapp_number,
        )

    @admin.display(description="Interessado", ordering="name")
    def interested_summary(self, obj):
        contact = obj.email
        if obj.phone:
            contact = f"{obj.email} · {obj.phone}"
        return format_html(
            '<strong class="lead-person__name">{}</strong>'
            '<span class="lead-person__contact">{}</span>',
            obj.name,
            contact,
        )

    @admin.display(description="Imóvel", ordering="property_title")
    def property_summary(self, obj):
        title = obj.property_title or "Interesse geral"
        if obj.property:
            location = " · ".join(
                value for value in (obj.property.neighborhood, obj.property.city) if value
            )
            if location:
                return format_html(
                    '<strong class="lead-property__title">{}</strong>'
                    '<span class="lead-property__location">{}</span>',
                    title,
                    location,
                )
        return format_html('<strong class="lead-property__title">{}</strong>', title)

    @admin.display(description="Situação", ordering="status")
    def status_summary(self, obj):
        return format_html(
            '<span class="lead-status lead-status--{}">{}</span>'
            '<span class="lead-priority lead-priority--{}">Prioridade {}</span>',
            obj.status,
            obj.get_status_display(),
            obj.priority,
            obj.get_priority_display().lower(),
        )

    @admin.display(description="Responsável", ordering="responsible__username")
    def responsible_summary(self, obj):
        if not obj.responsible:
            return format_html('<span class="lead-muted">Não definido</span>')
        return obj.responsible.get_full_name() or obj.responsible.username

    @admin.display(description="Situação", ordering="status")
    def status_badge(self, obj):
        return format_html(
            '<span class="lead-status lead-status--{}">{}</span>', obj.status, obj.get_status_display()
        )

    @admin.display(description="Próxima ação")
    def next_action(self, obj):
        tasks = getattr(obj, "pending_tasks", None)
        task = tasks[0] if tasks else None
        if task is None:
            return format_html('<span class="lead-muted">Sem ação programada</span>')
        css_class = " lead-next-action--overdue" if task.is_overdue else ""
        return format_html(
            '<span class="lead-next-action{}">{} · {}</span>',
            css_class,
            task.get_kind_display(),
            timezone.localtime(task.due_at).strftime("%d/%m/%Y %H:%M"),
        )

    @admin.display(description="Recebido em", ordering="created_at")
    def received_at(self, obj):
        local_created_at = timezone.localtime(obj.created_at)
        return format_html(
            '<span class="lead-received__date">{}</span>'
            '<span class="lead-received__time">{}</span>',
            local_created_at.strftime("%d/%m/%Y"),
            local_created_at.strftime("%H:%M"),
        )

    @admin.display(description="Ações")
    def row_actions(self, obj):
        change_url = reverse("admin:leads_lead_change", args=(obj.pk,))
        links = [
            format_html('<a class="lead-row-action lead-row-action--open" href="{}">Abrir</a>', change_url),
            format_html('<a class="lead-row-action" href="mailto:{}" title="Enviar e-mail" aria-label="Enviar e-mail">E-mail</a>', obj.email),
        ]
        digits = "".join(character for character in obj.phone if character.isdigit())
        if digits:
            whatsapp_number = digits if digits.startswith("55") else f"55{digits}"
            links.insert(
                1,
                format_html('<a class="lead-row-action" href="tel:{}" title="Ligar" aria-label="Ligar">Ligar</a>', digits),
            )
            links.append(
                format_html(
                    '<a class="lead-row-action lead-row-action--whatsapp" href="https://wa.me/{}" target="_blank" rel="noopener" title="WhatsApp" aria-label="WhatsApp">WhatsApp</a>',
                    whatsapp_number,
                )
            )
        rendered_links = format_html_join(" ", "{}", ((link,) for link in links))
        return format_html('<span class="lead-row-actions">{}</span>', rendered_links)

    @admin.display(description="Próxima ação")
    def next_action_summary(self, obj):
        if not obj or not obj.pk:
            return "Nenhuma ação programada."
        task = obj.tasks.filter(status=LeadTask.Status.PENDING).order_by("due_at").first()
        if task is None:
            return "Nenhuma ação programada."
        label = "ATRASADA" if task.is_overdue else "Programada"
        return format_html(
            '<strong class="lead-next-action{}">{}:</strong> {} em {} — {}',
            " lead-next-action--overdue" if task.is_overdue else "",
            label,
            task.get_kind_display(),
            timezone.localtime(task.due_at).strftime("%d/%m/%Y às %H:%M"),
            task.notes or "sem observação",
        )

    def changelist_view(self, request, extra_context=None):
        base = self.model.objects.filter(
            anonymized_at__isnull=True
        ).exclude(status=Lead.Status.DISCARDED)
        counts = base.aggregate(
            new=Count("id", filter=Q(status=Lead.Status.NEW), distinct=True),
            in_progress=Count(
                "id", filter=Q(status=Lead.Status.IN_PROGRESS), distinct=True
            ),
            visits=Count(
                "id", filter=Q(status=Lead.Status.VISIT_SCHEDULED), distinct=True
            ),
            completed=Count(
                "id", filter=Q(status=Lead.Status.COMPLETED), distinct=True
            ),
        )
        active_filter_chips = []
        filter_options = {
            "status__exact": ("Situação", dict(Lead.Status.choices)),
            "priority__exact": ("Prioridade", dict(Lead.Priority.choices)),
            "source__exact": ("Origem", dict(Lead.Source.choices)),
            "next_action": (
                "Próxima ação",
                {
                    "overdue": "Atrasadas",
                    "today": "Hoje",
                    "upcoming": "Futuras",
                    "none": "Sem próxima ação",
                },
            ),
        }
        for parameter, (title, choices) in filter_options.items():
            value = request.GET.get(parameter)
            if not value:
                continue
            remaining = request.GET.copy()
            remaining.pop(parameter, None)
            active_filter_chips.append(
                {
                    "title": title,
                    "value": choices.get(value, value),
                    "remove_url": f"?{remaining.urlencode()}" if remaining else "?",
                }
            )
        responsible_id = request.GET.get("responsible__id__exact")
        if responsible_id:
            responsible_name = get_user_model().objects.filter(pk=responsible_id).values_list(
                "username", flat=True
            ).first() or responsible_id
            remaining = request.GET.copy()
            remaining.pop("responsible__id__exact", None)
            active_filter_chips.append(
                {
                    "title": "Responsável",
                    "value": responsible_name,
                    "remove_url": f"?{remaining.urlencode()}" if remaining else "?",
                }
            )
        extra_context = {
            **(extra_context or {}),
            "lead_counts": counts,
            "active_filter_chips": active_filter_chips,
        }
        return super().changelist_view(request, extra_context=extra_context)

    def save_model(self, request, obj, form, change):
        previous = Lead.objects.filter(pk=obj.pk).first() if change else None
        if not change:
            obj.source = Lead.Source.MANUAL
            obj.status = Lead.Status.NEW
            obj.property_title = obj.property.title if obj.property else "Interesse geral"
            obj.consent_version = ""
            obj.consent_at = None
            if obj.responsible_id is None:
                obj.responsible = request.user
        if obj.status == Lead.Status.COMPLETED and obj.completed_at is None:
            obj.completed_at = timezone.now()
        elif obj.status != Lead.Status.COMPLETED:
            obj.completed_at = None
        super().save_model(request, obj, form, change)
        if previous and previous.status != obj.status:
            LeadInteraction.objects.create(
                lead=obj,
                kind=LeadInteraction.Kind.STATUS_CHANGE,
                description=f"Situação alterada de {previous.get_status_display()} para {obj.get_status_display()}.",
                created_by=request.user,
            )
        if previous and previous.responsible_id != obj.responsible_id:
            old_name = str(previous.responsible) if previous.responsible else "sem responsável"
            new_name = str(obj.responsible) if obj.responsible else "sem responsável"
            LeadInteraction.objects.create(
                lead=obj,
                kind=LeadInteraction.Kind.ASSIGNMENT,
                description=f"Responsável alterado de {old_name} para {new_name}.",
                created_by=request.user,
            )
        if previous and (
            previous.status != obj.status or previous.responsible_id != obj.responsible_id
        ):
            Lead.objects.filter(pk=obj.pk).update(last_interaction_at=timezone.now())

    def save_formset(self, request, form, formset, change):
        existing_task_status = {task.pk: task.status for task in LeadTask.objects.filter(lead=form.instance)}
        instances = formset.save(commit=False)
        for deleted in formset.deleted_objects:
            deleted.delete()
        for instance in instances:
            if isinstance(instance, LeadInteraction):
                instance.created_by = request.user
                instance.save()
                Lead.objects.filter(pk=form.instance.pk).update(last_interaction_at=instance.occurred_at)
            elif isinstance(instance, LeadTask):
                if instance.created_by_id is None:
                    instance.created_by = request.user
                if instance.responsible_id is None:
                    instance.responsible = form.instance.responsible or request.user
                was_completed = existing_task_status.get(instance.pk) == LeadTask.Status.COMPLETED
                if instance.status == LeadTask.Status.COMPLETED and not was_completed:
                    instance.completed_at = timezone.now()
                elif instance.status != LeadTask.Status.COMPLETED:
                    instance.completed_at = None
                instance.save()
                if instance.status == LeadTask.Status.COMPLETED and not was_completed:
                    LeadInteraction.objects.create(
                        lead=form.instance,
                        kind=LeadInteraction.Kind.TASK_COMPLETED,
                        description=f"Tarefa concluída: {instance.get_kind_display()}.",
                        outcome=instance.notes,
                        created_by=request.user,
                    )
                    Lead.objects.filter(pk=form.instance.pk).update(
                        last_interaction_at=timezone.now()
                    )
        formset.save_m2m()

    @admin.display(description="Retenção até")
    def retention_date(self, obj):
        return obj.retention_deadline

    def get_actions(self, request):
        actions = super().get_actions(request)
        is_administrator = request.user.is_superuser or request.user.groups.filter(name=ADMINISTRATOR_GROUP).exists()
        if not is_administrator:
            actions.pop("anonymize_selected", None)
        return actions

    @admin.action(description="Anonimizar contatos selecionados")
    def anonymize_selected(self, request, queryset):
        is_administrator = request.user.is_superuser or request.user.groups.filter(name=ADMINISTRATOR_GROUP).exists()
        if not is_administrator:
            return
        processed = sum(anonymize_lead(lead) for lead in queryset.iterator())
        self.message_user(request, f"{processed} contato(s) anonimizado(s).")

    def has_add_permission(self, request):
        return super().has_add_permission(request)

    def has_delete_permission(self, request, obj=None):
        return request.user.is_superuser or request.user.groups.filter(name=ADMINISTRATOR_GROUP).exists()

    def delete_view(self, request, object_id, extra_context=None):
        if request.method == "POST":
            reason = request.POST.get("removal_reason", "").strip()
            confirmed = request.POST.get("confirm_removal") == "yes"
            if not reason or not confirmed:
                if not reason:
                    messages.error(request, "Informe o motivo da remoção.")
                if not confirmed:
                    messages.error(request, "Marque a confirmação antes de remover.")
                submitted_data = request.POST
                request.POST = QueryDict()
                try:
                    return super().delete_view(
                        request,
                        object_id,
                        extra_context={
                            **(extra_context or {}),
                            "removal_reason_value": reason,
                        },
                    )
                finally:
                    request.POST = submitted_data
        return super().delete_view(request, object_id, extra_context=extra_context)

    def log_deletions(self, request, queryset):
        reason = request.POST.get("removal_reason", "").strip()
        if not reason:
            return super().log_deletions(request, queryset)
        return LogEntry.objects.log_actions(
            user_id=request.user.pk,
            queryset=queryset,
            action_flag=DELETION,
            change_message=f"Motivo da remoção: {reason}",
        )

    @admin.action(description="Exportar contatos selecionados em CSV")
    def export_csv(self, request, queryset):
        response = HttpResponse(content_type="text/csv; charset=utf-8")
        response["Content-Disposition"] = 'attachment; filename="contatos-chindler.csv"'
        response.write("\ufeff")
        writer = csv.writer(response, delimiter=";")
        writer.writerow(["Nome", "Telefone", "E-mail", "Imóvel", "Situação", "Responsável", "Recebido em"])
        for lead in queryset.select_related("responsible"):
            writer.writerow([
                lead.name, lead.phone, lead.email, lead.property_title, lead.get_status_display(),
                (lead.responsible.get_full_name() or lead.responsible.username) if lead.responsible else "",
                lead.created_at.isoformat(),
            ])
        return response

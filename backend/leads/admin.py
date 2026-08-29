import csv

from django import forms
from django.contrib import admin
from django.db.models import Count, Prefetch, Q
from django.http import HttpResponse
from django.utils import timezone
from django.utils.html import format_html

from properties.roles import ADMINISTRATOR_GROUP

from .models import Lead, LeadInteraction, LeadTask
from .services import anonymize_lead


class LeadAdminForm(forms.ModelForm):
    class Meta:
        model = Lead
        fields = "__all__"

    def clean(self):
        cleaned_data = super().clean()
        if cleaned_data.get("status") == Lead.Status.DISCARDED and not cleaned_data.get(
            "discard_reason", ""
        ).strip():
            self.add_error("discard_reason", "Informe o motivo do descarte.")
        return cleaned_data


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
    list_display = (
        "name",
        "property_title",
        "status_badge",
        "responsible",
        "next_action",
        "created_at",
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
    list_select_related = ("property", "responsible")
    list_per_page = 25
    date_hierarchy = "created_at"
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
            {"fields": (("status", "priority"), ("responsible", "source"), "next_action_summary", "discard_reason", ("last_interaction_at", "completed_at"))},
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
            return "—"
        css_class = " lead-next-action--overdue" if task.is_overdue else ""
        return format_html(
            '<span class="lead-next-action{}">{} · {}</span>',
            css_class,
            task.get_kind_display(),
            timezone.localtime(task.due_at).strftime("%d/%m/%Y %H:%M"),
        )

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
        now = timezone.now()
        base = self.model.objects.filter(
            anonymized_at__isnull=True
        ).exclude(status=Lead.Status.DISCARDED)
        counts = base.aggregate(
            new=Count("id", filter=Q(status=Lead.Status.NEW)),
            in_progress=Count("id", filter=Q(status=Lead.Status.IN_PROGRESS)),
            visits=Count("id", filter=Q(status=Lead.Status.VISIT_SCHEDULED)),
            overdue=Count("id", filter=Q(tasks__status=LeadTask.Status.PENDING, tasks__due_at__lt=now), distinct=True),
        )
        extra_context = {**(extra_context or {}), "lead_counts": counts}
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

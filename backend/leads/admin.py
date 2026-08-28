import csv

from django.contrib import admin
from django.http import HttpResponse

from properties.roles import ADMINISTRATOR_GROUP

from .models import Lead
from .services import anonymize_lead


@admin.register(Lead)
class LeadAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "property_title",
        "status",
        "responsible",
        "phone",
        "email",
        "created_at",
        "retention_date",
    )
    list_filter = ("status", "responsible", "anonymized_at", "created_at")
    search_fields = ("name", "email", "phone", "property_title")
    list_select_related = ("property", "responsible")
    readonly_fields = (
        "property",
        "property_title",
        "name",
        "phone",
        "email",
        "message",
        "consent_version",
        "consent_at",
        "created_at",
        "updated_at",
        "anonymized_at",
    )
    fields = (
        "property",
        "property_title",
        "name",
        "phone",
        "email",
        "message",
        "status",
        "responsible",
        "last_interaction_at",
        "consent_version",
        "consent_at",
        "created_at",
        "updated_at",
        "anonymized_at",
    )
    actions = ("export_csv", "anonymize_selected")

    @admin.display(description="Retenção até")
    def retention_date(self, obj):
        return obj.retention_deadline

    def get_actions(self, request):
        actions = super().get_actions(request)
        is_administrator = request.user.is_superuser or request.user.groups.filter(
            name=ADMINISTRATOR_GROUP
        ).exists()
        if not is_administrator:
            actions.pop("anonymize_selected", None)
        return actions

    @admin.action(description="Anonimizar contatos selecionados")
    def anonymize_selected(self, request, queryset):
        is_administrator = request.user.is_superuser or request.user.groups.filter(
            name=ADMINISTRATOR_GROUP
        ).exists()
        if not is_administrator:
            return
        processed = sum(anonymize_lead(lead) for lead in queryset.iterator())
        self.message_user(request, f"{processed} contato(s) anonimizado(s).")

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return request.user.is_superuser or request.user.groups.filter(
            name=ADMINISTRATOR_GROUP
        ).exists()

    @admin.action(description="Exportar contatos selecionados em CSV")
    def export_csv(self, request, queryset):
        response = HttpResponse(content_type="text/csv; charset=utf-8")
        response["Content-Disposition"] = 'attachment; filename="contatos-chindler.csv"'
        response.write("\ufeff")
        writer = csv.writer(response, delimiter=";")
        writer.writerow(
            ["Nome", "Telefone", "E-mail", "Imóvel", "Situação", "Responsável", "Recebido em"]
        )
        for lead in queryset.select_related("responsible"):
            writer.writerow(
                [
                    lead.name,
                    lead.phone,
                    lead.email,
                    lead.property_title,
                    lead.get_status_display(),
                    lead.responsible.get_full_name() or lead.responsible.username
                    if lead.responsible
                    else "",
                    lead.created_at.isoformat(),
                ]
            )
        return response

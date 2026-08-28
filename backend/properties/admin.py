import csv

from django.contrib import admin, messages
from django.core.exceptions import ValidationError
from django.forms.models import BaseInlineFormSet
from django.http import HttpResponse
from django.utils.html import format_html

from chindler_backend.forms import EmailOrUsernameAuthenticationForm

from .models import Property, PropertyChange, PropertyImage
from .roles import ADMINISTRATOR_GROUP
from .services import (
    change_property_status,
    move_property_to_trash,
    property_changes,
    property_snapshot,
    record_property_change,
    restore_property,
)


class PropertyImageInlineFormSet(BaseInlineFormSet):
    def clean(self):
        if any(self.errors):
            return

        active_forms = [
            form
            for form in self.forms
            if form.cleaned_data and not form.cleaned_data.get("DELETE", False)
        ]
        used_orders = set()
        for form in active_forms:
            order = form.cleaned_data.get("order", 0)
            if order in used_orders:
                if not form.instance._state.adding:
                    raise ValidationError(
                        "Cada imagem existente deve possuir uma ordem diferente."
                    )
                order = 0
                while order in used_orders:
                    order += 1
                form.cleaned_data["order"] = order
                form.instance.order = order
            used_orders.add(order)

        super().clean()
        if len(active_forms) > 20:
            raise ValidationError("Cada imóvel pode ter no máximo 20 imagens.")
        if sum(bool(form.cleaned_data.get("is_cover")) for form in active_forms) > 1:
            raise ValidationError("Selecione apenas uma imagem principal.")


class PropertyImageInline(admin.TabularInline):
    model = PropertyImage
    formset = PropertyImageInlineFormSet
    fields = (
        "preview",
        "image",
        "alt_text",
        "order",
        "is_cover",
        "dimensions",
        "formatted_file_size",
    )
    readonly_fields = ("preview", "dimensions", "formatted_file_size")
    extra = 1
    max_num = 20
    classes = ("collapse",)

    def get_formset(self, request, obj=None, **kwargs):
        formset = super().get_formset(request, obj, **kwargs)
        formset.form.base_fields["order"].help_text = (
            "Use 0 para a primeira foto. Ordens repetidas em novas imagens "
            "serão ajustadas automaticamente."
        )
        return formset

    @admin.display(description="Prévia")
    def preview(self, obj):
        if not obj or not obj.image:
            return "—"
        return format_html(
            '<img src="{}" alt="" style="width:110px;height:76px;object-fit:cover;border-radius:4px">',
            obj.thumbnail_url,
        )

    @admin.display(description="Dimensões")
    def dimensions(self, obj):
        if not obj or not obj.width or not obj.height:
            return "—"
        return f"{obj.width} × {obj.height} px"

    @admin.display(description="Tamanho")
    def formatted_file_size(self, obj):
        if not obj or not obj.file_size:
            return "—"
        return f"{obj.file_size / 1024:.0f} KB"


class PropertyChangeInline(admin.TabularInline):
    model = PropertyChange
    fields = ("action", "actor", "changes", "created_at")
    readonly_fields = fields
    extra = 0
    can_delete = False
    classes = ("collapse",)
    verbose_name_plural = "Histórico de alterações"

    def has_add_permission(self, request, obj=None):
        return False


class TrashFilter(admin.SimpleListFilter):
    title = "lixeira"
    parameter_name = "trash"

    def lookups(self, request, model_admin):
        return (("active", "Ativos"), ("trashed", "Na lixeira"))

    def queryset(self, request, queryset):
        if self.value() == "trashed":
            return queryset.filter(deleted_at__isnull=False)
        if self.value() == "active":
            return queryset.filter(deleted_at__isnull=True)
        return queryset


@admin.register(Property)
class PropertyAdmin(admin.ModelAdmin):
    list_display = (
        "title",
        "purpose",
        "property_type",
        "status",
        "neighborhood",
        "formatted_price",
        "is_featured",
        "updated_at",
        "trash_state",
    )
    list_filter = (
        TrashFilter,
        "status",
        "purpose",
        "property_type",
        "is_featured",
        "city",
        "neighborhood",
    )
    search_fields = ("title", "description", "street", "neighborhood", "city")
    ordering = ("-is_featured", "featured_order", "-created_at")
    readonly_fields = (
        "public_id",
        "status",
        "published_at",
        "archived_at",
        "deleted_at",
        "created_by",
        "updated_by",
        "created_at",
        "updated_at",
    )
    fieldsets = (
        (
            "Informações principais",
            {
                "fields": ("title", "description", "purpose", "property_type", "status"),
                "classes": ("collapse",),
            },
        ),
        (
            "Valores",
            {
                "fields": ("price", "show_price", "condominium_fee"),
                "classes": ("collapse",),
            },
        ),
        (
            "Características",
            {
                "fields": (
                    "total_area",
                    ("bedrooms", "suites", "bathrooms", "parking_spaces"),
                ),
                "classes": ("collapse",),
            },
        ),
        (
            "Endereço",
            {
                "fields": (
                    "street",
                    "number",
                    "complement",
                    "neighborhood",
                    "city",
                    "state",
                    "postal_code",
                    "address_visibility",
                ),
                "classes": ("collapse",),
            },
        ),
        (
            "Mapa e privacidade",
            {
                "fields": ("map_visibility",),
                "classes": ("collapse",),
            },
        ),
        (
            "Destaque",
            {
                "fields": ("is_featured", "featured_order"),
                "classes": ("collapse",),
            },
        ),
        (
            "Controle",
            {
                "fields": (
                    "published_at",
                    "archived_at",
                    "deleted_at",
                    "created_by",
                    "updated_by",
                    "created_at",
                    "updated_at",
                ),
                "classes": ("collapse",),
            },
        ),
    )
    inlines = (PropertyImageInline, PropertyChangeInline)
    actions = (
        "publish_selected",
        "move_to_draft",
        "mark_reserved",
        "mark_sold",
        "mark_rented",
        "archive_selected",
        "trash_selected",
        "restore_selected",
        "delete_permanently",
        "export_csv",
    )
    save_on_top = True

    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        form.base_fields["street"].label = "Rua"
        return form

    @admin.display(description="Preço", ordering="price")
    def formatted_price(self, obj):
        if not obj.show_price:
            return "Sob consulta"
        return f"R$ {obj.price:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

    @admin.display(description="Lixeira", boolean=True)
    def trash_state(self, obj):
        return obj.deleted_at is not None

    def save_model(self, request, obj, form, change):
        before = None
        if change:
            before = property_snapshot(Property.objects.get(pk=obj.pk))
        else:
            obj.created_by = request.user
        obj.updated_by = request.user
        obj.full_clean()
        super().save_model(request, obj, form, change)

        if before is None:
            record_property_change(obj, request.user, PropertyChange.Action.CREATED)
        else:
            changes = property_changes(before, property_snapshot(obj))
            if changes:
                record_property_change(
                    obj, request.user, PropertyChange.Action.UPDATED, changes
                )

    def delete_model(self, request, obj):
        move_property_to_trash(obj, request.user)

    def delete_queryset(self, request, queryset):
        for property_item in queryset:
            move_property_to_trash(property_item, request.user)

    def get_actions(self, request):
        actions = super().get_actions(request)
        is_administrator = request.user.is_superuser or request.user.groups.filter(
            name=ADMINISTRATOR_GROUP
        ).exists()
        if not is_administrator:
            actions.pop("delete_permanently", None)
        return actions

    def apply_status(self, request, queryset, status):
        updated = 0
        for property_item in queryset:
            try:
                change_property_status(property_item, status, request.user)
                updated += 1
            except ValidationError as exc:
                self.message_user(
                    request, f"{property_item.title}: {' '.join(exc.messages)}", messages.ERROR
                )
        if updated:
            self.message_user(request, f"{updated} imóvel(is) atualizado(s).", messages.SUCCESS)

    @admin.action(description="Publicar imóveis selecionados")
    def publish_selected(self, request, queryset):
        self.apply_status(request, queryset, Property.Status.PUBLISHED)

    @admin.action(description="Retirar da publicação e voltar para rascunho")
    def move_to_draft(self, request, queryset):
        self.apply_status(request, queryset, Property.Status.DRAFT)

    @admin.action(description="Marcar como reservado")
    def mark_reserved(self, request, queryset):
        self.apply_status(request, queryset, Property.Status.RESERVED)

    @admin.action(description="Marcar como vendido")
    def mark_sold(self, request, queryset):
        self.apply_status(request, queryset, Property.Status.SOLD)

    @admin.action(description="Marcar como alugado")
    def mark_rented(self, request, queryset):
        self.apply_status(request, queryset, Property.Status.RENTED)

    @admin.action(description="Arquivar imóveis selecionados")
    def archive_selected(self, request, queryset):
        self.apply_status(request, queryset, Property.Status.ARCHIVED)

    @admin.action(description="Enviar imóveis selecionados para a lixeira")
    def trash_selected(self, request, queryset):
        for property_item in queryset:
            move_property_to_trash(property_item, request.user)
        self.message_user(request, "Imóveis enviados para a lixeira.", messages.SUCCESS)

    @admin.action(description="Restaurar imóveis selecionados")
    def restore_selected(self, request, queryset):
        for property_item in queryset:
            restore_property(property_item, request.user)
        self.message_user(request, "Imóveis restaurados.", messages.SUCCESS)

    @admin.action(description="Excluir definitivamente imóveis da lixeira")
    def delete_permanently(self, request, queryset):
        is_administrator = request.user.is_superuser or request.user.groups.filter(
            name=ADMINISTRATOR_GROUP
        ).exists()
        if not is_administrator:
            self.message_user(request, "Ação não autorizada.", messages.ERROR)
            return
        trashed = queryset.filter(deleted_at__isnull=False)
        for property_item in trashed:
            record_property_change(
                property_item, request.user, PropertyChange.Action.DELETED
            )
        deleted_count = trashed.count()
        trashed.delete()
        self.message_user(
            request, f"{deleted_count} imóvel(is) excluído(s) definitivamente.", messages.SUCCESS
        )

    @admin.action(description="Exportar imóveis selecionados em CSV")
    def export_csv(self, request, queryset):
        response = HttpResponse(content_type="text/csv; charset=utf-8")
        response["Content-Disposition"] = 'attachment; filename="imoveis-chindler.csv"'
        response.write("\ufeff")
        writer = csv.writer(response, delimiter=";")
        writer.writerow(
            ["Título", "Finalidade", "Tipo", "Situação", "Bairro", "Cidade", "Preço", "Destaque"]
        )
        for item in queryset:
            writer.writerow(
                [
                    item.title,
                    item.get_purpose_display(),
                    item.get_property_type_display(),
                    item.get_status_display(),
                    item.neighborhood,
                    item.city,
                    item.price,
                    "Sim" if item.is_featured else "Não",
                ]
            )
        return response


@admin.register(PropertyChange)
class PropertyChangeAdmin(admin.ModelAdmin):
    list_display = ("property_title", "action", "actor", "created_at")
    list_filter = ("action", "created_at")
    search_fields = ("property_title", "actor__username", "actor__email")
    readonly_fields = ("property", "property_title", "actor", "action", "changes", "created_at")

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


admin.site.site_header = "Balcão de Imóveis"
admin.site.site_title = "Balcão de Imóveis"
admin.site.index_title = "Balcão de Imóveis"
admin.site.site_url = None
admin.site.login_form = EmailOrUsernameAuthenticationForm

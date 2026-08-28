from decimal import Decimal

from django.core.exceptions import ValidationError
from django.db import transaction
from django.utils import timezone

from .models import Property, PropertyChange


TRACKED_FIELDS = (
    "title",
    "description",
    "purpose",
    "property_type",
    "status",
    "price",
    "show_price",
    "condominium_fee",
    "total_area",
    "bedrooms",
    "suites",
    "bathrooms",
    "parking_spaces",
    "street",
    "number",
    "complement",
    "neighborhood",
    "city",
    "state",
    "postal_code",
    "address_visibility",
    "map_visibility",
    "is_featured",
    "featured_order",
)


def serialize_value(value):
    if isinstance(value, Decimal):
        return str(value)
    return value


def property_snapshot(property_item):
    return {
        field: serialize_value(getattr(property_item, field))
        for field in TRACKED_FIELDS
    }


def property_changes(before, after):
    return {
        field: {"anterior": before[field], "novo": after[field]}
        for field in TRACKED_FIELDS
        if before[field] != after[field]
    }


def record_property_change(property_item, actor, action, changes=None):
    return PropertyChange.objects.create(
        property=property_item,
        property_title=property_item.title,
        actor=actor,
        action=action,
        changes=changes or {},
    )


@transaction.atomic
def change_property_status(property_item, status, actor):
    if status == Property.Status.PUBLISHED:
        property_item.full_clean()
        errors = property_item.publication_errors()
        if errors:
            raise ValidationError(
                "Não foi possível publicar. Verifique: " + ", ".join(errors) + "."
            )

    previous_status = property_item.status
    property_item.status = status
    property_item.updated_by = actor
    update_fields = ["status", "updated_by", "updated_at"]
    if status == Property.Status.PUBLISHED and property_item.published_at is None:
        property_item.published_at = timezone.now()
        update_fields.append("published_at")
    if status == Property.Status.ARCHIVED:
        property_item.archived_at = timezone.now()
        update_fields.append("archived_at")
    property_item.save(update_fields=update_fields)
    record_property_change(
        property_item,
        actor,
        PropertyChange.Action.STATUS_CHANGED,
        {"status": {"anterior": previous_status, "novo": status}},
    )


@transaction.atomic
def move_property_to_trash(property_item, actor):
    if property_item.deleted_at is not None:
        return
    property_item.deleted_at = timezone.now()
    property_item.updated_by = actor
    property_item.save(update_fields=["deleted_at", "updated_by", "updated_at"])
    record_property_change(property_item, actor, PropertyChange.Action.TRASHED)


@transaction.atomic
def restore_property(property_item, actor):
    if property_item.deleted_at is None:
        return
    property_item.deleted_at = None
    property_item.updated_by = actor
    property_item.save(update_fields=["deleted_at", "updated_by", "updated_at"])
    record_property_change(property_item, actor, PropertyChange.Action.RESTORED)

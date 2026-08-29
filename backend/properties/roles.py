from django.contrib.auth.models import Group, Permission
from django.db.models.signals import post_migrate


ADMINISTRATOR_GROUP = "Administrador"
EDITOR_GROUP = "Editor"


def ensure_default_roles(**_kwargs):
    administrator, _ = Group.objects.get_or_create(name=ADMINISTRATOR_GROUP)
    editor, _ = Group.objects.get_or_create(name=EDITOR_GROUP)

    editor_permissions = Permission.objects.filter(
        content_type__app_label__in={"properties", "leads"},
        codename__in={
            "add_property",
            "change_property",
            "delete_property",
            "view_property",
            "add_propertyimage",
            "change_propertyimage",
            "delete_propertyimage",
            "view_propertyimage",
            "view_propertychange",
            "add_lead",
            "change_lead",
            "view_lead",
            "add_leadinteraction",
            "view_leadinteraction",
            "add_leadtask",
            "change_leadtask",
            "view_leadtask",
        },
    )
    editor.permissions.set(editor_permissions)

    administrator_permissions = Permission.objects.filter(
        content_type__app_label__in={"properties", "leads", "auth"}
    )
    administrator.permissions.set(administrator_permissions)


def register_role_setup():
    post_migrate.connect(
        ensure_default_roles,
        dispatch_uid="properties.ensure_default_roles",
    )

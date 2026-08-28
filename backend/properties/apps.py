from django.apps import AppConfig


class PropertiesConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "properties"
    verbose_name = "Imóveis"

    def ready(self):
        from .roles import register_role_setup
        from . import signals  # noqa: F401

        register_role_setup()

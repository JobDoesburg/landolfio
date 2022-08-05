from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class InventoryConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "inventory"
    verbose_name = _("Inventory")
    default = True

    def ready(self):
        """Import the signals when the app is ready."""
        # pylint: disable=unused-import,import-outside-toplevel
        from . import signals

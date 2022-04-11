"""The Django apps for the inventory module."""
from django.apps import AppConfig


class InventoryConfig(AppConfig):
    """Inventory app config."""

    default_auto_field = "django.db.models.BigAutoField"
    name = "inventory"

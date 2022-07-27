"""The Django apps concerning accounting."""
from threading import Event

from django.apps import AppConfig

shutting_down = Event()


class AccountingConfig(AppConfig):
    """Accounting app config."""

    default_auto_field = "django.db.models.BigAutoField"
    name = "accounting"
    verbose_name = "boekhouding"

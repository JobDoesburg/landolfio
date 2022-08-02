from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class MoneybirdConfig(AppConfig):
    """Inventory app config."""

    default_auto_field = "django.db.models.BigAutoField"
    name = "moneybird"
    verbose_name = _("moneybird")
    default = True

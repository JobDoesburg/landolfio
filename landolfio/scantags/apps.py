from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class ScanTagsConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "scantags"
    verbose_name = _("🔖 Scan tags")
    default = True

from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class NinoxImportConfig(AppConfig):

    default_auto_field = "django.db.models.BigAutoField"
    name = "ninox_import"
    verbose_name = _("Ninox import")

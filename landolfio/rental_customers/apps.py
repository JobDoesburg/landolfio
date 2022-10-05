from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class RentalCustomersConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "rental_customers"
    verbose_name = _("Rental customers")
    default = True

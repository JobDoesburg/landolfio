from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class NewRentalCustomersConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "new_rental_customers"
    verbose_name = _("New rental customers")
    default = True

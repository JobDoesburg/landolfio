from django.conf import settings
from django.utils.translation import gettext_lazy as _

from rental_customers.models import RegisteredRentalCustomer
from website.email import send_email


def send_new_customer_notification(obj):
    """Email the admin when a new customer registers."""
    send_email(
        to=settings.NOTIFICATION_EMAIL,
        subject=_("New customer registration: {}").format(obj.contact),
        txt_template="email/new-customer.txt",
        html_template="email/new-customer.html",
        context={
            "obj": obj,
            "count": RegisteredRentalCustomer.objects.filter(processed=False).count(),
        },
    )

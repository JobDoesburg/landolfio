from django.conf import settings
from django.template import loader
from django.utils.translation import gettext_lazy as _

from accounting.models import Contact
from new_customers.models import NewCustomer
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
            "count": NewCustomer.objects.filter(closed=False).count(),
        },
    )


def send_sepa_mandate_request(obj):
    """Send a SEPA mandate request to the customer."""
    obj.contact.request_payments_mandate(
        message=loader.render_to_string(
            "email/mandate_request_message.txt",
            {"customer": obj.contact},
        )
    )


def detect_duplicate_contact(contact: Contact):
    """Detect duplicate contacts."""
    all_contacts = Contact.objects.all()

    if contact.id:
        all_contacts = all_contacts.exclude(id=contact.id)

    matching_contacts = all_contacts.filter(
        email=contact.email, first_name=contact.first_name, last_name=contact.last_name
    )
    if matching_contacts.exists():
        return matching_contacts.first()
    return None

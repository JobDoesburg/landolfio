from django.conf import settings
from django.template import loader
from django.utils.translation import gettext_lazy as _

from accounting.models import Workflow, WorkflowTypes
from accounting.models.estimate import Estimate, EstimateDocumentLine
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


def process(obj):
    """Process the customer registration."""
    obj.processed = True
    obj.save()


def send_sepa_mandate_request(obj):
    """Send a SEPA mandate request to the customer."""
    obj.contact.request_payments_mandate(
        message=loader.render_to_string(
            "email/mandate_request_message.txt", {"customer": obj.contact}
        )
    )


def create_draft_agreement(obj):
    """Create a draft agreement for the customer."""

    assets = obj.assets.all()
    workflow = Workflow.objects.filter(
        active=True,
        type=WorkflowTypes.ESTIMATE_WORKFLOW,
        is_rental=True,
        is_direct_debit=obj.wants_sepa_mandate,
    ).first()

    estimate = Estimate.objects.create(
        contact=obj.contact,
        workflow=workflow,
    )
    for asset in assets:
        estimate.document_lines.create(
            description=asset.last_accounting_description or f"{asset.id}: TODO",
            price=asset.last_accounting_price or asset.listing_price or 0,
        )

    estimate.save()
    obj.agreement = estimate
    obj.save()
    estimate.push_to_moneybird()

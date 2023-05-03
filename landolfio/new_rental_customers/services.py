from accounting.models import Workflow, WorkflowTypes
from accounting.models.estimate import Estimate


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
            description=asset.last_accounting_description or f"{asset.name}: TODO",
            price=asset.last_accounting_price or asset.listing_price or 0,
        )

    estimate.save()
    obj.agreement = estimate
    obj.save()
    estimate.push_to_moneybird()

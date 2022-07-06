import threading

from django.conf import settings

from accounting.moneybird.administration import HttpsAdministration
from accounting.moneybird.synchronization import MoneybirdSync
from accounting.moneybird_resources import *

from accounting.moneybird.resource_types import (
    SynchronizableMoneybirdResourceType,
)

sync_lock = threading.Lock()


def sync_moneybird(full_sync=False) -> None:
    """
    Synchronize the database to the remote MoneyBird administration.

    Get changes from the remote MoneyBird administration and apply them in the database.

    This function expects the following Django settings to be set:
     - MONEYBIRD_ADMINISTRATION_ID
     - MONEYBIRD_API_KEY
    """
    resource_types = [
        LedgerAccountResourceType,  # These should be first
        WorkflowResourceType,
        ContactResourceType,
        SalesInvoiceResourceType,
        PurchaseInvoiceDocumentResourceType,
        ReceiptResourceType,
        GeneralJournalDocumentResourceType,
        ProductResourceType,
        EstimateResourceType,
        RecurringSalesInvoiceResourceType,
    ]

    # pylint: disable=consider-using-with
    locked = sync_lock.acquire(blocking=False)
    if locked:
        try:
            administration_id = settings.MONEYBIRD_ADMINISTRATION_ID
            key = settings.MONEYBIRD_API_KEY
            administration = HttpsAdministration(key, administration_id)

            if full_sync:
                for resource_type in resource_types:
                    if issubclass(resource_type, SynchronizableMoneybirdResourceType):
                        resource_type.get_queryset().update(moneybird_version=None)

            MoneybirdSync(administration).perform_sync(resource_types)
        finally:
            sync_lock.release()

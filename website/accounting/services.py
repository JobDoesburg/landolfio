import threading

from django.conf import settings

from accounting.moneybird.administration import HttpsAdministration
from accounting.moneybird.synchronization import MoneybirdSync
from accounting.moneybird_resources import *

sync_lock = threading.Lock()


def sync_moneybird() -> None:
    """
    Synchronize the database to the remote MoneyBird administration.

    Get changes from the remote MoneyBird administration and apply them in the database.

    This function expects the following Django settings to be set:
     - MONEYBIRD_ADMINISTRATION_ID
     - MONEYBIRD_API_KEY
    """
    resource_types = [
        SalesInvoiceResourceType,
        PurchaseInvoiceDocumentResourceType,
        ReceiptResourceType,
        GeneralJournalDocumentResourceType,
        ContactResourceType,
        LedgerAccountResourceType,
        ProductResourceType,
        EstimateResourceType,
        RecurringSalesInvoiceResourceType,
        WorkflowResourceType,
    ]

    # pylint: disable=consider-using-with
    locked = sync_lock.acquire(blocking=False)
    if locked:
        try:
            administration_id = settings.MONEYBIRD_ADMINISTRATION_ID
            key = settings.MONEYBIRD_API_KEY
            administration = HttpsAdministration(key, administration_id)

            MoneybirdSync(administration).perform_sync(resource_types)
        finally:
            sync_lock.release()

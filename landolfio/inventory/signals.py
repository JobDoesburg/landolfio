from django.db import models
from django.dispatch import receiver

from accounting.models.sales_invoice import SalesInvoiceDocumentLine
from accounting.models.purchase_document import PurchaseDocumentLine
from accounting.models.general_journal_document import (
    GeneralJournalDocumentLine,
    GeneralJournalDocument,
)
from accounting.models.recurring_sales_invoice import RecurringSalesInvoiceDocumentLine
from accounting.models.journal_document import JournalDocumentLine
from accounting.models.estimate import EstimateDocumentLine
from inventory.models.asset import Asset
from inventory.services import (
    find_assets_in_document_line,
    relink_document_lines_to_asset,
)


@receiver(
    models.signals.post_save,
    sender=JournalDocumentLine,
    dispatch_uid="journal_document_line_post_save",
)
def on_journal_document_line_post_save(
    sender, instance: JournalDocumentLine, *args, **kwargs
):
    # pylint: disable=unused-argument
    find_assets_in_document_line(instance)


@receiver(
    models.signals.post_save,
    sender=SalesInvoiceDocumentLine,
    dispatch_uid="sales_invoice_document_line_post_save",
)
def on_sales_invoice_document_line_post_save(
    sender, instance: SalesInvoiceDocumentLine, *args, **kwargs
):
    # pylint: disable=unused-argument
    find_assets_in_document_line(instance)


@receiver(
    models.signals.post_save,
    sender=PurchaseDocumentLine,
    dispatch_uid="purchase_document_line_post_save",
)
def on_purchase_document_line_post_save(
    sender, instance: PurchaseDocumentLine, *args, **kwargs
):
    # pylint: disable=unused-argument
    find_assets_in_document_line(instance)


@receiver(
    models.signals.post_save,
    sender=GeneralJournalDocumentLine,
    dispatch_uid="general_journal_document_line_post_save",
)
def on_general_journal_document_line_post_save(
    sender, instance: GeneralJournalDocumentLine, *args, **kwargs
):
    # pylint: disable=unused-argument
    find_assets_in_document_line(instance)


@receiver(
    models.signals.post_save,
    sender=RecurringSalesInvoiceDocumentLine,
    dispatch_uid="recurring_sales_invoice_document_line_post_save",
)
def on_recurring_sales_invoice_document_line_post_save(
    sender, instance: RecurringSalesInvoiceDocumentLine, *args, **kwargs
):
    # pylint: disable=unused-argument
    find_assets_in_document_line(instance)


@receiver(
    models.signals.post_save,
    sender=EstimateDocumentLine,
    dispatch_uid="estimate_document_line_post_save",
)
def on_estimate_document_line_post_save(
    sender, instance: EstimateDocumentLine, *args, **kwargs
):
    # pylint: disable=unused-argument
    find_assets_in_document_line(instance)


@receiver(
    models.signals.post_save,
    sender=GeneralJournalDocument,
    dispatch_uid="general_journal_document_post_save",
)
def on_general_journal_document_post_save(
    sender, instance: GeneralJournalDocument, *args, **kwargs
):
    # pylint: disable=unused-argument
    for line in instance.document_lines.all():
        find_assets_in_document_line(line)


@receiver(models.signals.post_save, sender=Asset, dispatch_uid="asset_post_save")
def on_asset_save(sender, instance: Asset, created, **kwargs):
    # pylint: disable=unused-argument
    if created:
        relink_document_lines_to_asset(instance)


# TODO subscription document lines

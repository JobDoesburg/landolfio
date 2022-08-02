import logging

from django.db import models
from django.dispatch import receiver

from accounting.models.sales_invoice import SalesInvoiceDocumentLine
from accounting.models.purchase_document import PurchaseDocumentLine
from accounting.models.general_journal_document import GeneralJournalDocumentLine, GeneralJournalDocument
from accounting.models.recurring_sales_invoice import RecurringSalesInvoiceDocumentLine
from accounting.models.journal_document import JournalDocumentLine
from accounting.models.estimate import EstimateDocumentLine
from inventory.models.asset import Asset
from inventory.services import (
    find_assets_in_document_line,
    relink_document_lines_to_asset,
)

logging.info("Loading inventory.models.signals")


@receiver(
    models.signals.post_save,
    sender=JournalDocumentLine,
    dispatch_uid="journal_document_line_post_save",
)
def on_document_line_save(sender, instance: JournalDocumentLine, *args, **kwargs):
    # pylint: disable=unused-argument
    logging.info("JournalDocumentLine post save")
    find_assets_in_document_line(instance)


@receiver(
    models.signals.post_save,
    sender=SalesInvoiceDocumentLine,
    dispatch_uid="sales_invoice_document_line_post_save",
)
def on_document_line_save(sender, instance: SalesInvoiceDocumentLine, *args, **kwargs):
    # pylint: disable=unused-argument
    logging.info("SalesInvoiceDocumentLine post save")
    find_assets_in_document_line(instance)


@receiver(
    models.signals.post_save,
    sender=PurchaseDocumentLine,
    dispatch_uid="purchase_document_line_post_save",
)
def on_document_line_save(sender, instance: PurchaseDocumentLine, *args, **kwargs):
    # pylint: disable=unused-argument
    logging.info("PurchaseDocumentLine post save")
    find_assets_in_document_line(instance)


@receiver(
    models.signals.post_save,
    sender=GeneralJournalDocumentLine,
    dispatch_uid="general_journal_document_line_post_save",
)
def on_document_line_save(sender, instance: GeneralJournalDocumentLine, *args, **kwargs):
    # pylint: disable=unused-argument
    logging.info("GeneralJournalDocumentLine post save")
    find_assets_in_document_line(instance)


@receiver(
    models.signals.post_save,
    sender=RecurringSalesInvoiceDocumentLine,
    dispatch_uid="recurring_sales_invoice_document_line_post_save",
)
def on_document_line_save(
    sender, instance: RecurringSalesInvoiceDocumentLine, *args, **kwargs
):
    # pylint: disable=unused-argument
    logging.info("RecurringSalesInvoiceDocumentLine post save")
    find_assets_in_document_line(instance)


@receiver(
    models.signals.post_save,
    sender=EstimateDocumentLine,
    dispatch_uid="estimate_document_line_post_save",
)
def on_document_line_save(sender, instance: EstimateDocumentLine, *args, **kwargs):
    # pylint: disable=unused-argument
    logging.info("EstimateDocumentLine post save")
    find_assets_in_document_line(instance)


@receiver(
    models.signals.post_save,
    sender=GeneralJournalDocument,
    dispatch_uid="general_journal_document_post_save",
)
def on_document_line_save(sender, instance: GeneralJournalDocument, *args, **kwargs):
    # pylint: disable=unused-argument
    logging.info("GeneralJournalDocument post save")
    for line in instance.document_lines.all():
        find_assets_in_document_line(line)


@receiver(models.signals.post_save, sender=Asset, dispatch_uid="asset_post_save")
def on_asset_save(sender, instance: Asset, created, **kwargs):
    logging.info("Asset post save")
    # pylint: disable=unused-argument
    if created:
        relink_document_lines_to_asset(instance)


# TODO subscription document lines

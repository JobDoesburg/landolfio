from django.db import models
from django.dispatch import receiver

from accounting.models import (
    SalesInvoiceDocumentLine,
    PurchaseDocumentLine,
    GeneralJournalDocumentLine,
    RecurringSalesInvoiceDocumentLine,
    GeneralJournalDocument,
)
from accounting.models.estimate import EstimateDocumentLine
from accounting.models.journal_document import JournalDocumentLine
from inventory.models.asset import Asset
from inventory.services import (
    find_assets_in_document_line,
    relink_document_lines_to_asset,
)


@receiver(models.signals.post_save, sender=JournalDocumentLine)
def on_document_line_save(sender, instance: JournalDocumentLine, **kwargs):
    # pylint: disable=unused-argument
    find_assets_in_document_line(instance)


@receiver(models.signals.post_save, sender=SalesInvoiceDocumentLine)
def on_document_line_save(sender, instance: SalesInvoiceDocumentLine, **kwargs):
    # pylint: disable=unused-argument
    find_assets_in_document_line(instance)


@receiver(models.signals.post_save, sender=PurchaseDocumentLine)
def on_document_line_save(sender, instance: PurchaseDocumentLine, **kwargs):
    # pylint: disable=unused-argument
    find_assets_in_document_line(instance)


@receiver(models.signals.post_save, sender=GeneralJournalDocumentLine)
def on_document_line_save(sender, instance: GeneralJournalDocumentLine, **kwargs):
    # pylint: disable=unused-argument
    find_assets_in_document_line(instance)


@receiver(models.signals.post_save, sender=RecurringSalesInvoiceDocumentLine)
def on_document_line_save(
    sender, instance: RecurringSalesInvoiceDocumentLine, **kwargs
):
    # pylint: disable=unused-argument
    find_assets_in_document_line(instance)


@receiver(models.signals.post_save, sender=EstimateDocumentLine)
def on_document_line_save(sender, instance: EstimateDocumentLine, **kwargs):
    # pylint: disable=unused-argument
    find_assets_in_document_line(instance)


@receiver(models.signals.post_save, sender=GeneralJournalDocument)
def on_document_line_save(sender, instance: GeneralJournalDocument, **kwargs):
    # pylint: disable=unused-argument
    for line in instance.document_lines.all():
        find_assets_in_document_line(line)


@receiver(models.signals.post_save, sender=Asset)
def on_asset_save(sender, instance: Asset, created, **kwargs):
    # pylint: disable=unused-argument
    if created:
        relink_document_lines_to_asset(instance)


# TODO subscription document lines

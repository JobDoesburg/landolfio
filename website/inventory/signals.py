"""Asset models."""
import logging
import re
from functools import lru_cache
from typing import Union

from django.db import models
from django.dispatch import receiver

from accounting.models.estimate import EstimateDocumentLine
from accounting.models.journal_document import JournalDocumentLine
from accounting.models.recurring_sales_invoice import RecurringSalesInvoiceDocumentLine
from inventory.models.asset import Asset


@lru_cache(maxsize=None)
def get_asset_ids():
    return set(Asset.objects.values_list("id", flat=True))


@lru_cache(maxsize=None)
def get_split_regex_pattern():
    delimiters = " ", ",", ":", ";", ".", "\n", "-", "\t", "\r"
    return "|".join(map(re.escape, delimiters))


def split_description(description: str) -> list[str]:
    return re.split(get_split_regex_pattern(), description)


def find_existing_asset_from_description(description: str) -> Union[Asset, None]:
    if description is None:
        return None

    asset_ids = get_asset_ids()
    words = set(split_description(description))
    matches = words.intersection(asset_ids)
    if len(matches) == 0:
        return None
    if len(matches) == 1:
        asset = find_asset_from_id(matches.pop())
        logging.info(f"Detected asset {asset} in '{description}'")
        return asset
    if len(matches) > 1:
        asset = find_asset_from_id(matches.pop())
        logging.warning(
            f"Multiple assets found for description '{description}', choosing {asset}"
        )  # TODO link to all assets
        return asset


def find_asset_id_from_description(description: str) -> Union[str, None]:
    if description is None:
        return None
    match = re.search(r"\[\s*([\w\d]+)\s*\]", description)
    if match is None:
        return None
    logging.info(f"Detected asset {match} in '{description}'.")
    return match.group(1)  # TODO link to all assets if multiple are found


def find_asset_from_id(asset_id) -> Union[Asset, None]:
    if asset_id is None:
        return None
    try:
        return Asset.objects.get(id=asset_id)
    except Asset.DoesNotExist:
        return None


def find_asset_in_document_lines(document_line):
    description = document_line.description
    # if (
    #     isinstance(document_line, JournalDocumentLine)
    #     and document_line.document.document_kind
    #     == DocumentKind.GENERAL_JOURNAL_DOCUMENT
    # ):
    #     if description is None:
    #         description = document_line.document.reference
    #     else:
    #         description += " " + document_line.document.reference

    asset_id = find_asset_id_from_description(description)
    asset_or_none = find_asset_from_id(asset_id)
    document_line.asset = asset_or_none
    document_line.asset_id_field = asset_id

    if asset_or_none is None:
        asset = find_existing_asset_from_description(description)
        if asset:
            document_line.asset = asset
            document_line.asset_id_field = asset.id


def link_asset_to_document_lines(document_lines, asset):
    for document_line in document_lines:
        document_line.asset = asset
        document_line.save()


@receiver(models.signals.post_save, sender=Asset)
def on_asset_save(sender, instance: Asset, **kwargs):
    # pylint: disable=unused-argument
    """Link DocumentLines to their asset upon asset creation."""
    asset_id = instance.id
    link_asset_to_document_lines(
        JournalDocumentLine.objects.filter(asset_id_field=asset_id), instance
    )
    link_asset_to_document_lines(
        EstimateDocumentLine.objects.filter(asset_id_field=asset_id), instance
    )
    link_asset_to_document_lines(
        RecurringSalesInvoiceDocumentLine.objects.filter(asset_id_field=asset_id),
        instance,
    )


@receiver(models.signals.pre_save, sender=JournalDocumentLine)
def on_document_line_save(sender, instance: JournalDocumentLine, **kwargs):
    # pylint: disable=unused-argument
    find_asset_in_document_lines(instance)


@receiver(models.signals.pre_save, sender=EstimateDocumentLine)
def on_document_line_save(sender, instance: EstimateDocumentLine, **kwargs):
    # pylint: disable=unused-argument
    find_asset_in_document_lines(instance)


@receiver(models.signals.pre_save, sender=RecurringSalesInvoiceDocumentLine)
def on_document_line_save(
    sender, instance: RecurringSalesInvoiceDocumentLine, **kwargs
):
    # pylint: disable=unused-argument
    find_asset_in_document_lines(instance)

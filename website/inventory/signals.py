import logging
import re
from decimal import Decimal
from functools import lru_cache
from typing import Union

from django.db import models
from django.dispatch import receiver

from accounting.models import (
    SalesInvoiceDocumentLine,
    PurchaseDocumentLine,
    GeneralJournalDocumentLine,
)
from accounting.models.journal_document import JournalDocumentLine
from inventory.models.asset import Asset, AssetOnJournalDocumentLine


@lru_cache(maxsize=None)
def get_asset_ids():
    return set(Asset.objects.values_list("id", flat=True))


@lru_cache(maxsize=None)
def get_split_regex_pattern():
    delimiters = " ", ",", ":", ";", ".", "\n", "-", "\t", "\r", "[", "]", "(", ")"
    return "|".join(map(re.escape, delimiters))


def split_description(description: str) -> list[str]:
    return re.split(get_split_regex_pattern(), description)


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


def find_existing_asset_from_description(
    description: str,
) -> Union[list[Asset], Asset, None]:
    if description is None:
        return None

    asset_ids = get_asset_ids()
    words = set(split_description(description))
    matches = words.intersection(asset_ids)

    assets = []
    for match in matches:
        asset = find_asset_from_id(match)
        if asset:
            logging.info(f"Detected asset {asset} in '{description}'")
            assets.append(asset)
    return assets


def link_asset_to_document_line(document_line, asset, value):
    return AssetOnJournalDocumentLine.objects.update_or_create(
        asset=asset, document_line=document_line, defaults={"value": value}
    )


def link_assets_to_document_line(document_line, assets):
    total_value = document_line.total_amount
    value = Decimal(round(document_line.total_amount / len(assets), 2))
    # TODO override behaviour for specific asset types (cellos en stokken)

    for index, asset in enumerate(assets):
        if index == len(assets) - 1:
            asset_value = total_value - value * (len(assets) - 1)
        else:
            asset_value = value
        link_asset_to_document_line(document_line, asset, asset_value)


def get_document_line_description(document_line):
    description = document_line.description
    if isinstance(document_line, GeneralJournalDocumentLine):
        if description is None:
            description = document_line.document.reference
        else:
            description += " " + document_line.document.reference
    return description


def find_assets_in_document_line(document_line):
    description = get_document_line_description(document_line)

    assets = find_existing_asset_from_description(description)

    if assets is None or len(assets) == 0:
        return
    if len(assets) == 1:
        link_asset_to_document_line(
            document_line, assets[0], document_line.total_amount
        )
    else:
        link_assets_to_document_line(document_line, assets)

    AssetOnJournalDocumentLine.objects.filter(document_line=document_line).exclude(
        asset__in=assets
    ).delete()


@receiver(models.signals.post_save, sender=SalesInvoiceDocumentLine)
def on_document_line_save(sender, instance: JournalDocumentLine, **kwargs):
    # pylint: disable=unused-argument
    find_assets_in_document_line(instance)


@receiver(models.signals.post_save, sender=PurchaseDocumentLine)
def on_document_line_save(sender, instance: JournalDocumentLine, **kwargs):
    # pylint: disable=unused-argument
    find_assets_in_document_line(instance)


@receiver(models.signals.post_save, sender=GeneralJournalDocumentLine)
def on_document_line_save(sender, instance: JournalDocumentLine, **kwargs):
    # pylint: disable=unused-argument
    find_assets_in_document_line(instance)


# TODO recurring sales invoice document lines
# TODO estimate document lines
# TODO subscription document lines
# TODO after creating new asset, link it to all existing document lines

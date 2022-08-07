import logging
import re
from decimal import Decimal
from functools import lru_cache
from typing import Union

from accounting.models import (
    SalesInvoiceDocumentLine,
    PurchaseDocumentLine,
    GeneralJournalDocumentLine,
    RecurringSalesInvoiceDocumentLine,
    JournalDocumentLine,
)
from accounting.models.estimate import EstimateDocumentLine
from inventory.models.asset import Asset
from inventory.models.asset_on_document_line import (
    AssetOnJournalDocumentLine,
    AssetOnEstimateDocumentLine,
    AssetOnRecurringSalesInvoiceDocumentLine,
)


@lru_cache(maxsize=None)
def get_asset_ids():
    return set(Asset.objects.values_list("id", flat=True))


@lru_cache(maxsize=None)
def get_split_regex_pattern():
    delimiters = " ", ",", ":", ";", ".", "\n", "-", "\t", "\r", "[", "]", "(", ")"
    return "|".join(map(re.escape, delimiters))


def split_description(description: str) -> list[str]:
    return re.split(get_split_regex_pattern(), description)


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


def get_asset_on_document_line_class(document_line):
    if isinstance(document_line, JournalDocumentLine):
        return AssetOnJournalDocumentLine
    elif isinstance(document_line, EstimateDocumentLine):
        return AssetOnEstimateDocumentLine
    elif isinstance(document_line, RecurringSalesInvoiceDocumentLine):
        return AssetOnRecurringSalesInvoiceDocumentLine
    else:
        raise Exception(f"Unknown document line type {document_line}")


def link_asset_to_document_line(document_line, asset, value):
    get_asset_on_document_line_class(document_line).objects.update_or_create(
        document_line=document_line, asset=asset, defaults={"value": value}
    )


def link_assets_to_document_line(document_line, assets):
    if document_line.total_amount is None:
        total_value = Decimal(0)
    else:
        total_value = Decimal(document_line.total_amount)
    value = Decimal(
        round(total_value / len(assets), 2)
    )  # TODO this should be math.ceil
    # TODO override behaviour for specific asset types (cellos en stokken)

    for index, asset in enumerate(assets):
        if index == len(assets) - 1:
            asset_value = total_value - value * (
                len(assets) - 1
            )  # TODO this may not be negative
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

    get_asset_on_document_line_class(document_line).objects.filter(
        document_line=document_line
    ).exclude(asset__in=assets).delete()


def _relink_document_lines_to_asset(model, asset):
    for document_line in model.objects.filter(description__contains=asset.id):
        find_assets_in_document_line(document_line)

    if issubclass(model, GeneralJournalDocumentLine):
        for document_line in model.objects.filter(
            document__reference__contains=asset.id
        ):
            find_assets_in_document_line(document_line)


def relink_document_lines_to_asset(asset):
    for model in (
        SalesInvoiceDocumentLine,
        PurchaseDocumentLine,
        GeneralJournalDocumentLine,
        RecurringSalesInvoiceDocumentLine,
        EstimateDocumentLine,
    ):
        _relink_document_lines_to_asset(model, asset)


def _relink_document_lines_to_assets(model):
    for document_line in model.objects.all():
        find_assets_in_document_line(document_line)


def relink_document_lines_to_assets():
    for model in (
        SalesInvoiceDocumentLine,
        PurchaseDocumentLine,
        GeneralJournalDocumentLine,
        RecurringSalesInvoiceDocumentLine,
        EstimateDocumentLine,
    ):
        _relink_document_lines_to_assets(model)


def check_accounting_errors():
    for asset in Asset.objects.reverse():
        if asset.accounting_errors:
            yield asset, asset.accounting_errors

    # TODO check for global errors

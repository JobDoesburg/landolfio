import logging
import re
from decimal import Decimal
from functools import lru_cache
from typing import Union

from inventory.models.asset import Asset

MIN_ASSET_NAME_LENGTH_FOR_FUZZY_LINK = 3


@lru_cache(maxsize=None)
def get_asset_ids():
    return set(Asset.objects.values_list("name", flat=True))


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
        return Asset.objects.get(name=asset_id)
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


def find_unique_unlinked_asset_for_moneybird_name(
    moneybird_name: str, unlinked_assets=None
) -> tuple[Union[Asset, None], list[Asset]]:
    """
    Find the unique unlinked local Asset whose name appears as a whole word
    in the Moneybird name (so "V11" matches "Viool V11" but "V1" does not).
    Returns (asset_or_None, all_matches). When more than one local asset
    matches, the first element is None and the caller can inspect all_matches
    to decide what to do.
    """
    if not moneybird_name:
        return None, []

    if unlinked_assets is None:
        unlinked_assets = list(Asset.objects.filter(moneybird_asset_id__isnull=True))

    words_lower = {w.lower() for w in split_description(moneybird_name) if w}
    matches = [
        asset
        for asset in unlinked_assets
        if asset.name
        and len(asset.name.strip()) >= MIN_ASSET_NAME_LENGTH_FOR_FUZZY_LINK
        and asset.name.strip().lower() in words_lower
    ]

    if len(matches) == 1:
        return matches[0], matches
    return None, matches

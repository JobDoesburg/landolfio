import logging
import re
from decimal import Decimal
from functools import lru_cache
from typing import Union

from inventory.models.asset import Asset


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

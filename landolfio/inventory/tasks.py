import logging

from django.conf import settings
from django.db import transaction
from django.tasks import task
from django_scheduled_tasks import cron_task

from inventory.models.asset import Asset
from inventory.moneybird import MoneybirdAssetService
from inventory.services import (
    MIN_ASSET_NAME_LENGTH_FOR_FUZZY_LINK,
    find_unique_unlinked_asset_for_moneybird_name,
)

logger = logging.getLogger(__name__)


@cron_task(cron_schedule="0 3 * * *")  # 3 AM every day
@task
def sync_unlinked_moneybird_assets(**kwargs):
    """
    Fetch all Moneybird assets and link unlinked ones to local assets.
    Runs nightly at 3 AM.
    """
    if kwargs:
        logger.warning("Ignoring unexpected task kwargs: %s", sorted(kwargs))
    logger.info("Starting Moneybird asset sync task")

    mb = MoneybirdAssetService()

    # Track statistics
    stats = {
        "total_fetched": 0,
        "already_linked": 0,
        "newly_linked": 0,
        "unmatched": [],
    }

    # Fetch from both ledger accounts
    ledger_accounts = [
        settings.MONEYBIRD_MARGIN_ASSETS_LEDGER_ACCOUNT_ID,
        settings.MONEYBIRD_NOT_MARGIN_ASSETS_LEDGER_ACCOUNT_ID,
    ]
    ledger_accounts = [la for la in ledger_accounts if la]

    if not ledger_accounts:
        logger.error("No ledger accounts configured, skipping sync")
        return stats

    # Get all linked Moneybird IDs once (stored as BigInteger; compare as str throughout)
    linked_mb_ids = {
        str(mb_id)
        for mb_id in Asset.objects.filter(moneybird_asset_id__isnull=False).values_list(
            "moneybird_asset_id", flat=True
        )
    }

    # Get all unlinked local assets once (excluding empty/very short names)
    unlinked_local_assets = [
        asset
        for asset in Asset.objects.filter(moneybird_asset_id__isnull=True)
        if asset.name
        and len(asset.name.strip()) >= MIN_ASSET_NAME_LENGTH_FOR_FUZZY_LINK
    ]

    for ledger_account_id in ledger_accounts:
        logger.info(f"Fetching assets from ledger account {ledger_account_id}")

        try:
            assets = mb.list_assets(ledger_account_id=int(ledger_account_id))
        except Exception as e:
            logger.error(
                f"Failed to fetch assets from ledger account {ledger_account_id}: {e}"
            )
            continue

        logger.info(f"Found {len(assets)} assets in ledger account {ledger_account_id}")

        for mb_asset in assets:
            stats["total_fetched"] += 1
            mb_id = str(mb_asset["id"])
            mb_name = mb_asset.get("name", "")

            # Check if already linked
            if mb_id in linked_mb_ids:
                stats["already_linked"] += 1
                continue

            local_asset, matches = find_unique_unlinked_asset_for_moneybird_name(
                mb_name, unlinked_local_assets
            )

            if local_asset is not None:
                try:
                    # Link them atomically
                    with transaction.atomic():
                        local_asset.moneybird_asset_id = mb_id
                        local_asset.save(update_fields=["moneybird_asset_id"])
                        local_asset.refresh_from_moneybird()

                    # Remove from unlinked list and add to linked IDs
                    unlinked_local_assets.remove(local_asset)
                    linked_mb_ids.add(mb_id)

                    stats["newly_linked"] += 1
                    logger.info(
                        f"Linked asset '{local_asset.name}' to Moneybird ID {mb_id}"
                    )
                except Exception as e:
                    logger.error(
                        f"Failed to link asset '{local_asset.name}' to Moneybird ID {mb_id}: {e}"
                    )
                    stats["unmatched"].append(
                        {
                            "id": mb_id,
                            "name": mb_name,
                            "reason": "link_failed",
                            "error": str(e),
                        }
                    )

            elif len(matches) > 1:
                logger.warning(
                    f"Multiple local assets match '{mb_name}': {[a.name for a in matches]}, skipping auto-link"
                )
                stats["unmatched"].append(
                    {
                        "id": mb_id,
                        "name": mb_name,
                        "reason": "multiple_matches",
                        "matches": [a.name for a in matches],
                    }
                )
            else:
                stats["unmatched"].append({"id": mb_id, "name": mb_name})

    # Log summary
    logger.info(
        f"Sync complete: {stats['total_fetched']} fetched, "
        f"{stats['already_linked']} already linked, "
        f"{stats['newly_linked']} newly linked, "
        f"{len(stats['unmatched'])} unmatched"
    )

    if stats["unmatched"]:
        logger.info(f"Unmatched assets: {stats['unmatched']}")

    return stats

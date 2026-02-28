import logging

from moneybird.resource_types import MoneybirdResourceType
from moneybird.webhooks.events import WebhookEvent
from inventory.models.asset import Asset
from inventory.moneybird import MoneybirdAssetService

logger = logging.getLogger(__name__)


class AssetResourceType(MoneybirdResourceType):
    entity_type = "company_assets_asset"
    entity_type_name = "asset"
    api_path = "assets"
    public_path = "assets"
    model = Asset
    can_write = False
    can_delete = False
    can_do_full_sync = False

    @classmethod
    def get_model_kwargs(cls, data):
        return {"moneybird_asset_id": str(data["id"])}

    @classmethod
    def get_queryset(cls):
        return cls.model.objects.all()

    @classmethod
    def get_moneybird_ids(cls):
        return list(
            filter(
                None,
                cls.get_queryset().values_list("moneybird_asset_id", flat=True),
            )
        )

    @classmethod
    def process_webhook_event(
        cls,
        resource_id: str,
        data: dict,
        event: WebhookEvent,
    ):
        # If no data, the asset was deleted
        if not data:
            return cls.delete_from_moneybird(resource_id)

        # Check if asset already exists locally
        try:
            asset = cls.get_queryset().get(moneybird_asset_id=resource_id)
            asset.refresh_from_moneybird()

            # If this is a created event and the name doesn't match, update Moneybird
            if event.value == "company_assets_asset_created":
                moneybird_name = data.get("name", "")
                if moneybird_name and moneybird_name != asset.name:
                    logger.info(
                        f"Updating Moneybird asset name from '{moneybird_name}' to '{asset.name}'"
                    )
                    asset.update_on_moneybird()

            return asset
        except cls.model.DoesNotExist:
            # Asset doesn't exist locally - try to find by name and link
            moneybird_name = data.get("name", "")
            if not moneybird_name:
                logger.warning(f"Asset {resource_id} has no name, cannot match")
                return None

            # Try to find exact match (case-insensitive)
            try:
                asset = cls.get_queryset().get(
                    name__iexact=moneybird_name, moneybird_asset_id__isnull=True
                )
                logger.info(
                    f"Linking local asset '{asset.name}' to Moneybird asset {resource_id}"
                )
                asset.moneybird_asset_id = resource_id
                asset.save(update_fields=["moneybird_asset_id"])
                asset.refresh_from_moneybird()

                # Update Moneybird if names differ in case
                if moneybird_name != asset.name:
                    logger.info(
                        f"Updating Moneybird asset name from '{moneybird_name}' to '{asset.name}'"
                    )
                    asset.update_on_moneybird()

                return asset
            except cls.model.DoesNotExist:
                return None
            except cls.model.MultipleObjectsReturned:
                logger.warning(
                    f"Multiple assets found with name '{moneybird_name}', cannot auto-link"
                )
                return None

    @classmethod
    def delete_from_moneybird(cls, resource_id: str):
        try:
            asset = cls.get_queryset().get(moneybird_asset_id=resource_id)
            logger.info(
                f"Unlinking local asset '{asset.name}' from deleted Moneybird asset"
            )
            asset.moneybird_asset_id = None
            asset.moneybird_data = None
            asset.disposal = None
            asset.current_value = None
            asset.save(
                update_fields=[
                    "moneybird_asset_id",
                    "moneybird_data",
                    "disposal",
                    "current_value",
                ]
            )
        except cls.model.DoesNotExist:
            pass

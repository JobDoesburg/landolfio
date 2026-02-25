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
        logger.info(f"Processing {event} for {cls.entity_type_name} {resource_id}")

        if not data:
            return cls.delete_from_moneybird(resource_id)

        try:
            asset = cls.get_queryset().get(moneybird_asset_id=resource_id)
            logger.info(f"Asset {resource_id} already exists locally, refreshing")
            asset.refresh_from_moneybird()
            asset.update_on_moneybird()
            return asset
        except cls.model.DoesNotExist:
            asset_name = data.get("name", "")
            if asset_name:
                try:
                    asset = cls.get_queryset().get(
                        name=asset_name, moneybird_asset_id__isnull=True
                    )
                    logger.info(
                        f"Found existing asset with name '{asset_name}', linking to Moneybird asset {resource_id}"
                    )
                    asset.moneybird_asset_id = resource_id
                    asset._refresh_from_moneybird(data)
                    return asset
                except cls.model.DoesNotExist:
                    logger.info(
                        f"No existing asset found with name '{asset_name}' to link"
                    )
                except cls.model.MultipleObjectsReturned:
                    logger.warning(
                        f"Multiple assets found with name '{asset_name}', cannot auto-link"
                    )
            else:
                logger.warning(f"Asset {resource_id} has no name, cannot match")
            return None

    @classmethod
    def delete_from_moneybird(cls, resource_id: str):
        logger.info(f"Asset {resource_id} deleted on Moneybird")
        try:
            asset = cls.get_queryset().get(moneybird_asset_id=resource_id)
            logger.info(
                f"Unlinking local asset {asset.id} from Moneybird asset {resource_id}"
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
            logger.info(
                f"Asset {resource_id} not found locally, nothing to unlink"
            )
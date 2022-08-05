from inventory.models.category import AssetCategory
from inventory.models.location import AssetLocation
from inventory.models.collection import Collection
from inventory.models.asset import Asset


def get_extra_assets_context(context):
    context.update(
        {
            "categories": AssetCategory.objects.all().order_by("order"),
            "locations": AssetLocation.objects.all().order_by("order"),
            "collections": Collection.objects.all().order_by("order"),
            "recent_assets": Asset.objects.all().order_by("-created_at")[:10],
        }
    )
    return context

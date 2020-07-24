from polymorphic.admin import StackedPolymorphicInline

from asset_events.admin import AssetForeignKeyStackedInline
from sales.models import SingleAssetSale


class AssetSaleEventInline(StackedPolymorphicInline.Child):
    model = SingleAssetSale


class AssetSaleAssetInline(AssetForeignKeyStackedInline):  # TODO StatusChangingEventAdmin extend
    model = SingleAssetSale
    fk_name = "sale"
    extra = 0

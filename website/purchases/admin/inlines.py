from polymorphic.admin import StackedPolymorphicInline

from asset_events.admin import AssetForeignKeyStackedInline
from purchases.models.delivery import SingleAssetDelivery
from purchases.models.purchase import SingleAssetPurchase


class AssetPurchaseEventInline(StackedPolymorphicInline.Child):
    model = SingleAssetPurchase


class AssetPurchaseAssetInline(AssetForeignKeyStackedInline):  # TODO StatusChangingEventAdmin extend
    model = SingleAssetPurchase
    fk_name = "purchase"
    extra = 0


class AssetDeliveryEventInline(StackedPolymorphicInline.Child):
    model = SingleAssetDelivery


class AssetDeliveryAssetInline(AssetForeignKeyStackedInline):  # TODO StatusChangingEventAdmin extend
    model = SingleAssetDelivery
    fk_name = "delivery"
    extra = 0

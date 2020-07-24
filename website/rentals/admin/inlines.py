from polymorphic.admin import StackedPolymorphicInline

from asset_events.admin import AssetForeignKeyStackedInline
from rentals.models.issuance_unprocessed import SingleUnprocessedAssetIssuance
from rentals.models.issuance_loan import SingleAssetLoan
from rentals.models.issuance_rent import SingleAssetRental
from rentals.models.returnal import SingleAssetReturnal


class UnprocessedAssetIssuanceEventInline(StackedPolymorphicInline.Child):
    model = SingleUnprocessedAssetIssuance


class UnprocessedAssetIssuanceAssetInline(AssetForeignKeyStackedInline):  # TODO StatusChangingEventAdmin extend
    model = SingleUnprocessedAssetIssuance
    fk_name = "issuance"
    extra = 0


class AssetLoanEventInline(StackedPolymorphicInline.Child):
    model = SingleAssetLoan


class AssetLoanAssetInline(AssetForeignKeyStackedInline):  # TODO StatusChangingEventAdmin extend
    model = SingleAssetLoan
    fk_name = "loan"
    extra = 0


class AssetRentalEventInline(StackedPolymorphicInline.Child):
    model = SingleAssetRental


class AssetRentalAssetInline(AssetForeignKeyStackedInline):  # TODO StatusChangingEventAdmin extend
    model = SingleAssetRental
    fk_name = "rental"
    extra = 0


class AssetReturnalEventInline(StackedPolymorphicInline.Child):
    model = SingleAssetReturnal


class AssetReturnalAssetInline(AssetForeignKeyStackedInline):  # TODO StatusChangingEventAdmin extend
    model = SingleAssetReturnal
    fk_name = "returnal"
    extra = 0

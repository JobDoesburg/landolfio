from django.contrib import admin

from asset_events.admin import AssetForeignKeyAdmin, AssetForeignKeyStackedInline
from rentals.models.issuance_unprocessed import UnprocessedAssetIssuance, SingleUnprocessedAssetIssuance
from rentals.models.issuance_rent import AssetRental, SingleAssetRental
from rentals.models.issuance_loan import AssetLoan, SingleAssetLoan


class UnprocessedAssetIssuanceAssetInline(AssetForeignKeyStackedInline):  # TODO StatusChangingEventAdmin extend
    model = SingleUnprocessedAssetIssuance
    fk_name = "issuance"
    extra = 0


class AssetLoanAssetInline(AssetForeignKeyStackedInline):  # TODO StatusChangingEventAdmin extend
    model = SingleAssetLoan
    fk_name = "loan"
    extra = 0


class AssetRentalAssetInline(AssetForeignKeyStackedInline):  # TODO StatusChangingEventAdmin extend
    model = SingleAssetRental
    fk_name = "rental"
    extra = 0


@admin.register(UnprocessedAssetIssuance)
class UnprocessedAssetIssuancesAdmin(AssetForeignKeyAdmin):
    inlines = [UnprocessedAssetIssuanceAssetInline]

    class Media:
        """Necessary to use AutocompleteFilter."""


@admin.register(AssetRental)
class AssetRentalsAdmin(AssetForeignKeyAdmin):
    inlines = [AssetRentalAssetInline]

    class Media:
        """Necessary to use AutocompleteFilter."""


@admin.register(AssetLoan)
class AssetLoansAdmin(AssetForeignKeyAdmin):
    inlines = [AssetLoanAssetInline]

    class Media:
        """Necessary to use AutocompleteFilter."""

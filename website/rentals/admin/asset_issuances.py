from django.contrib import admin

from asset_events.admin import AssetForeignKeyAdmin
from rentals.admin.inlines import UnprocessedAssetIssuanceAssetInline, AssetRentalAssetInline, AssetLoanAssetInline
from rentals.models.issuance_unprocessed import UnprocessedAssetIssuance
from rentals.models.issuance_rent import AssetRental
from rentals.models.issuance_loan import AssetLoan


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

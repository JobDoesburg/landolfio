from asset_events.models import SingleStatusChangingEvent
from assets.models import Asset


class AssetAmortization(SingleStatusChangingEvent):
    class Meta:
        verbose_name = "amortization"
        verbose_name_plural = "amortizations"

    input_statuses = [
        Asset.UNKNOWN,
        Asset.PLACEHOLDER,
        Asset.TO_BE_DELIVERED,
        Asset.UNDER_REVIEW,
        Asset.MAINTENANCE_IN_HOUSE,
        Asset.MAINTENANCE_EXTERNAL,
        Asset.AVAILABLE,
        Asset.ISSUED_UNPROCESSED,
        Asset.ISSUED_RENT,
        Asset.ISSUED_LOAN,
    ]
    output_status = Asset.AMORTIZED

    # TODO post-save:
    #  Make a new moneybird memorial record taking it off the stock balance

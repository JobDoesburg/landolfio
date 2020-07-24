from asset_events.models import SingleStatusChangingEvent
from assets.models import Asset


class AssetReview(SingleStatusChangingEvent):
    class Meta:
        verbose_name = "review"
        verbose_name_plural = "reviews"

    input_statuses = [Asset.UNDER_REVIEW]
    output_status = Asset.AVAILABLE

    # TODO add some logic that validates the contents of Asset here

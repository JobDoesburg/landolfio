from django.db import models
from django.db.models import PROTECT

from asset_events.models import SingleStatusChangingEvent
from assets.models import Asset
from maintenance.models import MaintenanceProvider


class AssetMaintenanceTicket(SingleStatusChangingEvent):
    class Meta:
        verbose_name = "maintenance ticket"
        verbose_name_plural = "maintenance tickets"

    input_statuses = [
        Asset.UNDER_REVIEW,
        Asset.AVAILABLE,
        Asset.ISSUED_UNPROCESSED,
        Asset.ISSUED_LOAN,
        Asset.ISSUED_RENT,
    ]

    def get_output_status(self):
        return Asset.MAINTENANCE_EXTERNAL if self.maintenance_provider else Asset.MAINTENANCE_IN_HOUSE

    maintenance_provider = models.ForeignKey(MaintenanceProvider, null=True, blank=True, on_delete=PROTECT)


class AssetMaintenanceReturn(SingleStatusChangingEvent):
    class Meta:
        verbose_name = "maintenance return"
        verbose_name_plural = "maintenance returns"

    input_statuses = [Asset.MAINTENANCE_IN_HOUSE, Asset.MAINTENANCE_EXTERNAL]
    output_status = Asset.AVAILABLE

    # TODO add FK to a maintenance invoice/report?

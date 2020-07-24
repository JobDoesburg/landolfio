from polymorphic.admin import StackedPolymorphicInline

from maintenance.models.review import *
from maintenance.models.maintenance_ticket import *
from maintenance.models.amortization import *


class AssetReviewEventInline(StackedPolymorphicInline.Child):
    model = AssetReview


class AssetMaintenanceTicketEventInline(StackedPolymorphicInline.Child):
    model = AssetMaintenanceTicket


class AssetMaintenanceReturnEventInline(StackedPolymorphicInline.Child):
    model = AssetMaintenanceReturn


class AssetAmortizationEventInline(StackedPolymorphicInline.Child):
    model = AssetAmortization

from django.contrib import admin

from moneybird.models import SynchronizableMoneybirdResourceModel
from moneybird.resource_types import get_moneybird_resource_for_model


class MoneybirdResourceModelAdmin(admin.ModelAdmin):
    def get_readonly_fields(self, request, obj=None):
        readonly_fields = ("moneybird_id",)
        if issubclass(self.model, SynchronizableMoneybirdResourceModel):
            readonly_fields += ("moneybird_version",)
        return super().get_readonly_fields(request, obj) + readonly_fields

    def has_delete_permission(self, request, obj=None):
        if not get_moneybird_resource_for_model(self.model).can_delete:
            return False
        return super().has_delete_permission(request, obj)

    def has_add_permission(self, request):
        if not get_moneybird_resource_for_model(self.model).can_write:
            return False
        return super().has_delete_permission(request)

    def has_change_permission(self, request, obj=None):
        if not get_moneybird_resource_for_model(self.model).can_write:
            return False
        return super().has_change_permission(request, obj)

from django.contrib import admin
from django.db.models import Q
from nested_admin.nested import NestedModelAdmin

from asset_events.models import *


class AssetForeignKeyAdmin(NestedModelAdmin):
    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "asset":
            obj_id = request.resolver_match.kwargs.get("object_id")
            kwargs["queryset"] = Asset.objects.filter(Q(status__in=self.model.get_input_statuses()) | Q(id=obj_id))
            kwargs[
                "help_text"
            ] = f"You can only select assets with one of the following statuses: {', '.join(Asset.STATUS_CHOICES[x][1] for x in self.model.get_input_statuses())}."
        return super().formfield_for_foreignkey(db_field, request, **kwargs)


class AssetForeignKeyStackedInline(admin.StackedInline):
    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "asset":
            obj_id = request.resolver_match.kwargs.get("object_id")
            kwargs["queryset"] = Asset.objects.filter(Q(status__in=self.model.get_input_statuses()) | Q(id=obj_id))
            kwargs[
                "help_text"
            ] = f"You can only select assets with one of the following statuses: {', '.join(Asset.STATUS_CHOICES[x][1] for x in self.model.get_input_statuses())}."
        return super().formfield_for_foreignkey(db_field, request, **kwargs)


class AssetForeignKeyTabularInline(admin.TabularInline):
    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "asset":
            obj_id = request.resolver_match.kwargs.get("object_id")
            kwargs["queryset"] = Asset.objects.filter(Q(status__in=self.model.get_input_statuses()) | Q(id=obj_id))
            kwargs[
                "help_text"
            ] = f"You can only select assets with one of the following statuses: {', '.join(Asset.STATUS_CHOICES[x][1] for x in self.model.get_input_statuses())}."
        return super().formfield_for_foreignkey(db_field, request, **kwargs)


class StatusChangingEventAdmin(AssetForeignKeyAdmin):
    list_display = ["asset", "date", "memo", "created"]
    list_filter = ["asset__category", "asset__size"]


@admin.register(MiscellaneousAssetEvent)
class MiscellaneousAssetEventAdmin(StatusChangingEventAdmin):
    class Media:
        """Necessary to use AutocompleteFilter."""

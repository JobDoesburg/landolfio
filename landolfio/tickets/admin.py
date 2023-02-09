from autocompletefilter.admin import AutocompleteFilterMixin
from django.contrib import admin
from django.shortcuts import redirect
from django_easy_admin_object_actions.admin import ObjectActionsMixin
from django_easy_admin_object_actions.decorators import object_action
from django.utils.translation import gettext_lazy as _

from tickets.admin_filters import (
    ClosedTicketFilter,
    AssignedTicketFilter,
    DueTicketFilter,
)
from tickets.models import Ticket, TicketType


@admin.register(TicketType)
class TicketTypeAdmin(admin.ModelAdmin):
    search_fields = ["name"]

    readonly_fields = ["code_defined"]

    def has_change_permission(self, request, obj=None):
        if obj and obj.code_defined:
            return False
        return super().has_change_permission(request, obj)

    def has_delete_permission(self, request, obj=None):
        if obj and obj.code_defined:
            return False
        return super().has_delete_permission(request, obj)

    def get_search_results(self, request, queryset, search_term):
        queryset, use_distinct = super().get_search_results(
            request, queryset, search_term
        )
        queryset = queryset.exclude(code_defined=True)
        return queryset, use_distinct


@admin.register(Ticket)
class TicketAdmin(AutocompleteFilterMixin, ObjectActionsMixin, admin.ModelAdmin):
    date_hierarchy = "date_created"

    ordering = ["-date_due", "-id"]

    list_display = [
        "__str__",
        "ticket_type",
        "contact",
        "assets_str",
        "date_due",
        "date_closed",
        "assigned_to",
    ]

    list_display_links = ["__str__"]

    list_filter = [
        ClosedTicketFilter,
        AssignedTicketFilter,
        DueTicketFilter,
        "ticket_type",
    ]

    fields = [
        "ticket_type",
        "title",
        "contact",
        "description",
        "assets",
        "estimates",
        "sales_invoices",
        "date_due",
        "created_by",
        "assigned_to",
    ]

    autocomplete_fields = [
        "ticket_type",
        "assets",
        "contact",
        "estimates",
        "sales_invoices",
        "created_by",
        "assigned_to",
    ]

    readonly_fields = [
        "date_created",
        "date_updated",
        "date_closed",
        "created_by",
    ]

    object_actions_after_related_objects = [
        "close",
        "reopen",
    ]

    def assets(self, obj):
        return obj.assets.all()

    def assets_str(self, obj):
        return (
            ", ".join([str(asset.id) for asset in obj.assets.all()])
            if obj.assets.all()
            else None
        )

    assets_str.short_description = _("Assets")

    def get_readonly_fields(self, request, obj=None):
        """Make all fields readonly if ticket is closed."""
        if obj and obj.closed:
            return self.fields
        return super().get_readonly_fields(request, obj)

    def save_model(self, request, obj, form, change):
        """Set created_by field on new objects."""
        if not change:
            obj.created_by = request.user
        super().save_model(request, obj, form, change)

    @object_action(
        label=_("Close ticket"),
        extra_classes="default",
        log_message="Ticket closed",
        perform_after_saving=True,
        condition=lambda request, obj: not obj.closed,
        display_as_disabled_if_condition_not_met=True,
    )
    def close(self, _, obj):
        obj.close()
        return True

    @object_action(
        label=_("Reopen ticket"),
        extra_classes="default",
        log_message="Ticket reopened",
        perform_after_saving=True,
        condition=lambda request, obj: obj.closed,
        display_as_disabled_if_condition_not_met=True,
    )
    def reopen(self, request, obj):
        obj.reopen()
        return True

    def changeform_view(self, request, object_id=None, form_url="", extra_context=None):
        """Redirect to the change form from the subclass."""
        if object_id:
            try:
                obj = self.model.objects.select_subclasses().get(pk=object_id)
            except self.model.DoesNotExist:
                return super().changeform_view(
                    request, object_id, form_url, extra_context
                )
            obj_class = obj.__class__
            if issubclass(obj_class, self.model) and not obj_class == self.model:
                return redirect(
                    f"admin:{obj_class._meta.app_label}_{obj_class._meta.model_name}_change",
                    object_id=object_id,
                )
        return super().changeform_view(request, object_id, form_url, extra_context)

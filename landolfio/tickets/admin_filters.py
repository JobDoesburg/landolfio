from django.contrib import admin
from django.contrib.auth import get_user_model
from django.db.models import Q
from django.utils import timezone
from django.utils.translation import gettext_lazy as _


class ClosedTicketFilter(admin.SimpleListFilter):
    """Filter for closed tickets that defaults to open tickets."""

    title = _("status")
    parameter_name = "status"

    def choices(self, changelist):
        for lookup, title in self.lookup_choices:
            yield {
                "selected": self.value() == lookup
                or (self.value() is None and lookup == "open"),
                "query_string": changelist.get_query_string(
                    {self.parameter_name: lookup}, []
                ),
                "display": title,
            }

    def lookups(self, request, model_admin):
        return (
            ("open", _("Open")),
            ("all", _("All")),
            ("closed", _("Closed")),
        )

    def queryset(self, request, queryset):
        if self.value() == "all":
            return queryset
        if self.value() == "closed":
            return queryset.filter(closed=True)
        return queryset.filter(closed=False)


class AssignedTicketFilter(admin.SimpleListFilter):
    """Filter that defaults to tickets that are assigned to the current user or not assigned at all."""

    title = _("assignee")
    parameter_name = "assignee"

    def choices(self, changelist):
        yield {
            "selected": self.value() is None,
            "query_string": changelist.get_query_string(
                {self.parameter_name: None}, []
            ),
            "display": _("Unassigned or assigned to me"),
        }
        yield {
            "selected": self.value() == "all",
            "query_string": changelist.get_query_string(
                {self.parameter_name: "all"}, []
            ),
            "display": _("All"),
        }
        for lookup, title in self.lookup_choices:
            yield {
                "selected": self.value() == lookup,
                "query_string": changelist.get_query_string(
                    {self.parameter_name: lookup}, []
                ),
                "display": title,
            }

    def lookups(self, request, model_admin):
        for user in get_user_model().objects.all():
            yield user.id, user.get_full_name()

    def queryset(self, request, queryset):
        if self.value() == "all":
            return queryset
        if self.value() is None:
            return queryset.filter(
                Q(assigned_to=request.user) | Q(assigned_to__isnull=True)
            )
        return queryset.filter(assigned_to=self.value())


class DueTicketFilter(admin.SimpleListFilter):
    """Filter due tickets."""

    title = _("due")
    parameter_name = "due"

    def choices(self, changelist):
        yield {
            "selected": self.value() is None,
            "query_string": changelist.get_query_string(
                {self.parameter_name: None}, []
            ),
            "display": _("Due or no due date"),
        }
        yield {
            "selected": self.value() == "all",
            "query_string": changelist.get_query_string(
                {self.parameter_name: "all"}, []
            ),
            "display": _("All"),
        }
        for lookup, title in self.lookup_choices:
            yield {
                "selected": self.value() == lookup,
                "query_string": changelist.get_query_string(
                    {self.parameter_name: lookup}, []
                ),
                "display": title,
            }

    def lookups(self, request, model_admin):
        return (
            ("due", _("Due")),
            ("not_due", _("Not due")),
        )

    def queryset(self, request, queryset):
        if self.value() == "all":
            return queryset
        if self.value() == "due":
            return queryset.filter(date_due__lt=timezone.now())
        if self.value() == "not_due":
            return queryset.filter(date_due__gte=timezone.now())
        return queryset.filter(
            Q(date_due__lt=timezone.now()) | Q(date_due__isnull=True)
        )

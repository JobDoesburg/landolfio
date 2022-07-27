from django.contrib import admin, messages
from django.http import HttpResponseRedirect
from django.utils.safestring import mark_safe
from django.utils.translation import gettext as _, ngettext

from moneybird.models import (
    SynchronizableMoneybirdResourceModel,
    MoneybirdDocumentLineModel,
)
from moneybird.resource_types import (
    get_moneybird_resource_type_for_model,
    get_moneybird_resource_type_for_document_lines_model,
)
from moneybird.settings import settings


def push_to_moneybird(admin_obj, request, queryset):
    qs = queryset.filter(_synced_with_moneybird=False)
    errors = 0
    for obj in qs:
        try:
            admin_obj.push_to_moneybird()
        except Exception as e:
            admin_obj.message_user(
                request,
                _("Error pushing %s to Moneybird: %s") % (obj, e),
                messages.ERROR,
            )
            errors += 1

    successful = qs.count() - errors

    if successful >= 1:
        admin_obj.message_user(
            request,
            ngettext(
                "%d object was successfully pushed to Moneybird.",
                "%d objects were successfully pushed to Moneybird.",
                successful,
            )
            % successful,
            messages.SUCCESS,
        )


class MoneybirdResourceModelAdminMixin:
    def get_queryset(self, *args, **kwargs):
        return (
            super().get_queryset(*args, **kwargs).filter(_delete_from_moneybird=False)
        )

    @property
    def moneybird_resource_type(self):
        if issubclass(self.model, MoneybirdDocumentLineModel):
            return get_moneybird_resource_type_for_document_lines_model(self.model)
        return get_moneybird_resource_type_for_model(self.model)

    def get_readonly_fields(self, *args, **kwargs):
        readonly_fields = (
            "moneybird_id",
            "_synced_with_moneybird",
            "_delete_from_moneybird",
        )
        if issubclass(self.model, SynchronizableMoneybirdResourceModel):
            readonly_fields += ("moneybird_version",)
        return tuple(super().get_readonly_fields(*args, **kwargs)) + readonly_fields

    def has_delete_permission(self, *args, **kwargs):
        resource_type = self.moneybird_resource_type
        if resource_type and not resource_type.can_delete:
            return False
        return super().has_delete_permission(*args, **kwargs)

    def has_add_permission(self, *args, **kwargs):
        resource_type = self.moneybird_resource_type
        if resource_type and not resource_type.can_write:
            return False
        return super().has_delete_permission(*args, **kwargs)

    def has_change_permission(self, *args, **kwargs):
        resource_type = self.moneybird_resource_type
        if resource_type and not resource_type.can_write:
            return False
        return super().has_change_permission(*args, **kwargs)

    @admin.display(description="View on Moneybird")
    def view_on_moneybird(self, obj):
        url = obj.moneybird_url
        if url is None:
            return None
        return mark_safe(
            f'<a class="button small" href="{url}" target="_blank" style="white-space: nowrap;">View on Moneybird</a>'
        )

    def save_related(self, request, form, formsets, change):
        super().save_related(request, form, formsets, change)
        if settings.MONEYBIRD_AUTO_PUSH:
            obj = form.instance
            try:
                obj.push_to_moneybird()
            except Exception as e:
                self.message_user(
                    request, _("Error pushing to Moneybird: %s") % e, messages.ERROR
                )

    def get_actions(self, request):
        actions = super().get_actions(request)
        if self.has_change_permission(request):
            actions["push_to_moneybird"] = (
                push_to_moneybird,
                "push_to_moneybird",
                _(
                    "Push selected %s to Moneybird"
                    % self.model._meta.verbose_name_plural
                ),
            )
        return actions

    change_form_template = "moneybird/admin/change_form.html"

    def get_moneybird_actions(self, request, obj=None):
        return []

    def changeform_view(self, request, object_id=None, form_url="", extra_context=None):
        if object_id:
            obj = self.get_object(request, object_id)
        else:
            obj = None
        context = extra_context or {}
        context["moneybird_actions"] = self.get_moneybird_actions(request, obj)
        return super().changeform_view(
            request, object_id=None, form_url="", extra_context=context
        )

    def response_change(self, request, obj):
        for action in self.get_moneybird_actions(request, obj):
            if request.POST.get(action["post_parameter"]):
                return action["func"](self, request, obj)
        return super().response_change(request, obj)


class MoneybirdResourceModelAdmin(MoneybirdResourceModelAdminMixin, admin.ModelAdmin):
    pass
from django.contrib import admin
from django import forms
from django.utils.safestring import mark_safe

from moneybird.models import (
    SynchronizableMoneybirdResourceModel,
    MoneybirdDocumentLineModel,
)
from moneybird.resource_types import (
    get_moneybird_resource_for_model,
    get_moneybird_resource_for_document_lines_model,
)


class MoneybirdResourceModelForm(forms.ModelForm):
    def save(self, commit=True):
        if self.errors or not commit:
            return super().save(commit=commit)
        else:
            self.instance.save(push_to_moneybird=False)
            self._save_m2m()
        return self.instance


class MoneybirdResourceModelFormSet(forms.BaseModelFormSet):
    def delete_existing(self, obj, commit=True):
        if commit:
            obj.delete(delete_on_moneybird=False)

    def save_existing_objects(self, commit=True):
        saved_instances = super().save_existing_objects(commit=commit)
        print(self.deleted_objects)  # TODO batch delete those
        return saved_instances


class MoneybirdResourceModelAdmin(admin.ModelAdmin):

    # form = MoneybirdResourceModelForm
    # formset = MoneybirdResourceModelFormSet

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.obj = None

    @property
    def moneybird_resource_type_class(self):
        if issubclass(self.model, MoneybirdDocumentLineModel):
            return get_moneybird_resource_for_document_lines_model(self.model)
        return get_moneybird_resource_for_model(self.model)

    def get_readonly_fields(self, request, obj=None):
        readonly_fields = ("moneybird_id",)
        if issubclass(self.model, SynchronizableMoneybirdResourceModel):
            readonly_fields += ("moneybird_version",)
        return tuple(super().get_readonly_fields(request, obj)) + readonly_fields

    def has_delete_permission(self, request, obj=None):
        resource_type = self.moneybird_resource_type_class
        if resource_type and not resource_type.can_delete:
            return False
        return super().has_delete_permission(request, obj)

    def has_add_permission(self, request):
        resource_type = self.moneybird_resource_type_class
        if resource_type and not resource_type.can_write:
            return False
        return super().has_delete_permission(request)

    def has_change_permission(self, request, obj=None):
        resource_type = self.moneybird_resource_type_class
        if resource_type and not resource_type.can_write:
            return False
        return super().has_change_permission(request, obj)

    @admin.display(description="View on Moneybird")
    def view_on_moneybird(self, obj):
        url = obj.moneybird_url
        if url is None:
            return None
        return mark_safe(
            f'<a class="button small" href="{url}" target="_blank" style="white-space: nowrap;">View on Moneybird</a>'
        )


# def save_model(self, request, obj, form, change):
#     self.obj = obj
#     obj.save(push_to_moneybird=False)
#
# def save_related(self, request, form, formsets, change):
#     super().save_related(request, form, formsets, change)
#     self.obj.save(push_to_moneybird=True)

# TODO save_formset should get the push_to_moneybird argument and pass it through the formset.save() method so instances are not directly pushed

# TODO delete action should not call bulk delete but delete the objects individually

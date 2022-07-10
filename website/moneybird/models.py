from django.db import models
from django.db.models.utils import resolve_callables
from django.utils.translation import gettext as _

from moneybird.resource_types import (
    get_moneybird_resource_for_model,
    get_moneybird_resource_for_document_lines_model,
)


class MoneybirdResourceModel(models.Model):
    moneybird_id = models.PositiveBigIntegerField(
        verbose_name=_("Moneybird ID"), null=True, blank=True
    )

    class Meta:
        abstract = True

    @property
    def moneybird_resource_type_class(self):
        return get_moneybird_resource_for_model(self.__class__)

    @property
    def moneybird_document_line_parent_resource_type_class(self):
        return get_moneybird_resource_for_document_lines_model(self.__class__)

    def serialize_for_moneybird(self):
        if self.is_document_line_model:
            return self.document_line_parent.serialize_document_line_for_moneybird(
                self, self.document_line_parent
            )

        if self.moneybird_resource_type_class is None:
            return None

        return self.moneybird_resource_type_class.serialize_for_moneybird(self)

    @staticmethod
    def _calc_moneybird_data_diff(new_instance, old_instance):
        new_data = new_instance.serialize_for_moneybird()
        old_data = old_instance.serialize_for_moneybird()

        diff = {}
        for key, value in new_data.items():
            if key not in old_data or value != old_data[key]:
                diff[key] = value
        # TODO: removed resource_data is not handled yet
        return diff

    def update_fields_from_moneybird(self, data):
        fields_to_update = self.moneybird_resource_type_class.get_model_kwargs(data)
        for k, v in resolve_callables(fields_to_update):
            setattr(self, k, v)

    def push_diff_to_moneybird(self, instance):
        if self.moneybird_resource_type_class is None:
            return

        diff = self._calc_moneybird_data_diff(self, instance)
        if diff == {}:
            return

        return self.push_to_moneybird(diff)

    def push_to_moneybird(self, data=None):
        if self.moneybird_resource_type_class is None:
            return

        if data is None:
            self.moneybird_resource_type_class.push_to_moneybird(self)
        else:
            self.moneybird_resource_type_class.push_to_moneybird(self, data)

    def delete_on_moneybird(self):
        if self.moneybird_resource_type_class is None:
            return

        self.moneybird_resource_type_class.delete_from_moneybird(self)

    def refresh_from_moneybird(self):
        if self.moneybird_resource_type_class is None:
            return

        self.moneybird_resource_type_class.get_from_moneybird(self)

    @property
    def is_document_line_model(self):
        return (
            self.moneybird_resource_type_class is None
            and self.moneybird_document_line_parent_resource_type_class is not None
        )

    @property
    def document_line_parent(self):
        if not self.is_document_line_model:
            return None
        return getattr(
            self,
            self.moneybird_document_line_parent_resource_type_class.document_foreign_key,
        )

    def save(self, push_to_moneybird=True, *args, **kwargs):
        if push_to_moneybird:
            if self.moneybird_id is None:
                self.push_to_moneybird()
            else:
                old_object = self.__class__.objects.get(pk=self.pk)
                self.push_diff_to_moneybird(old_object)

        super().save(*args, **kwargs)

        if push_to_moneybird and self.is_document_line_model:
            parent = self.document_line_parent
            if parent is not None:
                parent.moneybird_resource_type_class.push_document_line_to_moneybird(
                    self, parent
                )

    def delete(self, delete_on_moneybird=True, *args, **kwargs):
        if delete_on_moneybird:
            self.delete_on_moneybird()

        super().delete(*args, **kwargs)

        if delete_on_moneybird and self.is_document_line_model:
            parent = self.document_line_parent
            if parent is not None:
                parent.moneybird_resource_type_class.delete_document_line_on_moneybird(
                    self, parent
                )


class SynchronizableMoneybirdResourceModel(MoneybirdResourceModel):
    moneybird_version = models.PositiveBigIntegerField(
        verbose_name=_("Moneybird version"), null=True, blank=True
    )

    class Meta:
        abstract = True

    def save(self, *args, **kwargs):
        old_object = self.__class__.objects.get(pk=self.pk)
        diff = self._calc_moneybird_data_diff(self, old_object)
        if diff != {}:
            self.moneybird_version = None

        return super().save(*args, **kwargs)

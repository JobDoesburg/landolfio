from django.conf import settings
from django.db import models
from django.db.models.utils import resolve_callables
from django.utils.translation import gettext as _

from moneybird.resource_types import (
    get_moneybird_resource_for_model,
    get_moneybird_resource_for_document_lines_model,
)


def auto_push_to_moneybird():
    return getattr(settings, "MONEYBIRD_AUTO_PUSH_TO_MONEYBIRD", True)


class MoneybirdResourceModel(models.Model):
    moneybird_id = models.PositiveBigIntegerField(
        verbose_name=_("Moneybird ID"), null=True, blank=True
    )

    class Meta:
        abstract = True

    @property
    def moneybird_resource_type_class(self):
        return get_moneybird_resource_for_model(self.__class__)

    def serialize_for_moneybird(self):
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
        self.push_to_moneybird(diff)

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

    def save(self, push_to_moneybird=auto_push_to_moneybird(), *args, **kwargs):
        if push_to_moneybird:
            if self.moneybird_id is None:
                self.push_to_moneybird()
            else:
                old_object = self.__class__.objects.get(pk=self.pk)
                self.push_diff_to_moneybird(old_object)

        return super().save(*args, **kwargs)

    def delete(self, delete_on_moneybird=auto_push_to_moneybird(), *args, **kwargs):
        if delete_on_moneybird:
            self.delete_on_moneybird()

        return super().delete(*args, **kwargs)


class MoneybirdDocumentLineModel(MoneybirdResourceModel):
    class Meta:
        abstract = True

    @property
    def moneybird_document_line_parent_resource_type_class(self):
        return get_moneybird_resource_for_document_lines_model(self.__class__)

    @property
    def document_line_parent(self):
        return getattr(
            self,
            self.moneybird_document_line_parent_resource_type_class.document_foreign_key,
        )

    def serialize_for_moneybird(self):
        if self.document_line_parent is None:
            return None
        return self.moneybird_document_line_parent_resource_type_class.serialize_document_line_for_moneybird(
            self, self.document_line_parent
        )

    def push_diff_to_moneybird(self, instance):
        if self.document_line_parent is None:
            return None

        diff = self._calc_moneybird_data_diff(self, instance)
        if diff == {}:
            return

        diff["id"] = self.moneybird_id  # For document lines, the id must always be set

        self.push_to_moneybird(diff)

    def push_to_moneybird(self, data=None):
        if self.document_line_parent is None:
            return None
        if data is None:
            self.moneybird_document_line_parent_resource_type_class.push_document_line_to_moneybird(
                self, self.document_line_parent
            )
        else:
            self.moneybird_document_line_parent_resource_type_class.push_document_line_to_moneybird(
                self, self.document_line_parent, data
            )

    def refresh_from_moneybird(self):
        if self.document_line_parent is None:
            return
        return self.document_line_parent.refresh_from_moneybird()

    def save(self, push_to_moneybird=auto_push_to_moneybird(), *args, **kwargs):
        if push_to_moneybird and self.document_line_parent is not None:
            if self.moneybird_id is None:
                old_parent = self.document_line_parent.__class__.objects.get(
                    pk=self.document_line_parent.pk
                )
                old_document_line_ids = set(
                    getattr(
                        old_parent,
                        self.moneybird_document_line_parent_resource_type_class.document_line_foreign_key,
                    ).values_list("pk", flat=True)
                )

                self.push_to_moneybird()  # This will actually save the document line upon receiving the new data from Moneybird

                new_document_line_ids = set(
                    getattr(
                        self.document_line_parent,
                        self.moneybird_document_line_parent_resource_type_class.document_line_foreign_key,
                    ).values_list("pk", flat=True)
                )
                new_pk = set(new_document_line_ids - old_document_line_ids).pop()
                self.pk = new_pk
            else:
                old_object = self.__class__.objects.get(pk=self.pk)
                self.push_diff_to_moneybird(old_object)

            self.refresh_from_db()

            return

        return super().save(push_to_moneybird=False, *args, **kwargs)

    def delete(self, delete_on_moneybird=auto_push_to_moneybird(), *args, **kwargs):
        if delete_on_moneybird and self.document_line_parent is not None:
            self.document_line_parent.moneybird_resource_type_class.delete_document_line_on_moneybird(
                self, self.document_line_parent
            )
        return super().delete(delete_on_moneybird=False, *args, **kwargs)

    def delete_on_moneybird(self):
        if self.document_line_parent is None:
            return
        self.document_line_parent.moneybird_resource_type_class.delete_document_line_on_moneybird(
            self, self.document_line_parent
        )

    def update_fields_from_moneybird(self, data):
        fields_to_update = self.moneybird_document_line_parent_resource_type_class.get_document_line_model_kwargs(
            data, self.document_line_parent
        )
        for k, v in resolve_callables(fields_to_update):
            setattr(self, k, v)


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

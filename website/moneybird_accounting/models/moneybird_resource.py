import datetime
from decimal import Decimal
from typing import Dict, Any

from django.core.checks import register, Error, Warning
from django.db import models
from django.conf import settings

# TODO create MoneybirdSimpleResourceModel for models without Synchronization endpoint:
# Entities you can only get:
# document_style, custom_field

# Entities you can get and post/patch but not sync
# identity (+/default),

# Entities that are MoneybirdSynchronizableResourceModel
# general document, general journal document, purchase invoice, receipt, typeless document


class MoneybirdResourceModel(models.Model):
    """Objects that refer to models in Moneybird and can be accessed via the API."""

    class Meta:
        abstract = True

    moneybird_resource_name = None

    @classmethod
    def get_moneybird_resource_name(cls):
        if cls.moneybird_resource_name:
            return cls.moneybird_resource_name
        else:
            raise NotImplementedError

    id = models.CharField(
        primary_key=True,
        max_length=20,
        help_text="This is the primary key of this object, both for this application and in Moneybird.",
        editable=False,
    )

    moneybird_data_fields = []  # Fields that are managed by Moneybird
    moneybird_readonly_data_fields = (
        []
    )  # Fields that are only written by Moneybird and should not be written by Django
    moneybird_foreign_key_fields = (
        {}
    )  # Fields that refer to another MoneybirdResourceModel, like invoices have contacts. Use only for fields that should be passed to the Moneybird API
    moneybird_nested_data_fields = (
        {}
    )  # Fields that are the reversed relation of another MoneybirdResourceModel that have a foreign key to this object

    @classmethod
    def check(cls, **kwargs):
        errors = super().check(**kwargs)
        moneybird_fields = cls.get_moneybird_fields()

        for field in moneybird_fields:
            if field not in dir(cls):
                errors.append(
                    Error(
                        "Moneybird field is not an attribute.",
                        hint="Remove the field from the Moneybird fields or add an attribute to the model..",
                        obj=field,
                        id="moneybird_accounting.models.E001",
                    )
                )

        for field in cls.get_moneybird_readonly_fields():
            if field not in moneybird_fields:
                errors.append(
                    Error(
                        "Moneybird read-only field is not a Moneybird field.",
                        hint="Remove the field from the read-only fields or add it to the moneybird data fields.",
                        obj=field,
                        id="moneybird_accounting.models.E002",
                    )
                )
        for field in cls.get_moneybird_foreign_key_fields():
            if field in moneybird_fields:
                errors.append(
                    Error(
                        "Moneybird foreign key field cannot be a regular Moneybird data field.",
                        hint="Either remove this field from the foreign key fields (and make sure the attribute returned by get_moneybird_attr() is JSON serializable), or remove it from the Moneybird data fields. Note: Django automatically creates the <field>_id attribute, that can be used for synchronizing foreign key objects!",
                        obj=field,
                        id="moneybird_accounting.models.E003",
                    )
                )
            if not f"{field}_id" in moneybird_fields:
                errors.append(
                    Warning(
                        "This model does not have <field>_id as Moneybird data field for this foreign key field.",
                        hint="Synchronizing foreign key objects might not work as expected.",
                        obj=field,
                        id="moneybird_accounting.models.W001",
                    )
                )
            if not issubclass(cls._meta.get_field(field).remote_field.model, MoneybirdResourceModel):
                errors.append(
                    Error(
                        "Moneybird foreign key field does not reference a MoneybirdResourceModel.",
                        hint="Either remove this field from the foreign key fields, or make the referred model a MoneybirdResourceModel!",
                        obj=field,
                        id="moneybird_accounting.models.E004",
                    )
                )

        for field in cls.get_moneybird_nested_data_fields():
            if field in moneybird_fields:
                errors.append(
                    Error(
                        "Moneybird nested data field cannot be a regular Moneybird data field.",
                        hint="Either remove this field from the nested data fields (and make sure the attribute returned by get_moneybird_attr() is JSON serializable), or remove it from the Moneybird data fields.",
                        obj=field,
                        id="moneybird_accounting.models.E005",
                    )
                )
            if not issubclass(cls.get_moneybird_nested_data_fields()[field], MoneybirdNestedDataResourceModel):
                errors.append(
                    Error(
                        "Moneybird nested data field does not reference a MoneybirdNestedDataResourceModel.",
                        hint="Either remove this field from the nested data fields, or make the referred model a MoneybirdNestedDataResourceModel!",
                        obj=field,
                        id="moneybird_accounting.models.E006",
                    )
                )

        return errors

    # TODO add sanity check whether the values above are in the correct subset of things etc

    @classmethod
    def get_moneybird_fields(cls):
        return cls.moneybird_data_fields + ["id"]

    @classmethod
    def get_moneybird_readonly_fields(cls):
        return cls.moneybird_readonly_data_fields + ["id"]

    @classmethod
    def get_moneybird_foreign_key_fields(cls):
        return cls.moneybird_foreign_key_fields

    @classmethod
    def get_moneybird_nested_data_fields(cls):
        return cls.moneybird_nested_data_fields

    processed = False  # If True, saving this object will not trigger a create or patch call to Moneybird. Used when synchronizing Moneybird objects.

    def get_moneybird_attr(self, field):
        if (
            field in self.get_moneybird_fields()
            or field in self.get_moneybird_foreign_key_fields()
            or field in self.get_moneybird_nested_data_fields()
        ):
            attr = getattr(self, field, None)
            if isinstance(attr, Decimal):
                attr = float(attr)
            elif isinstance(attr, datetime.date):
                attr = attr.isoformat()
            return attr

    def set_moneybird_attr(self, field, value):
        if field in self.get_moneybird_fields() or field in self.get_moneybird_foreign_key_fields():
            return setattr(self, field, value)

    def get_moneybird_resource_data(self):
        """Get a Moneybird-API supported data representation of this object."""
        result = {}
        for field in self.get_moneybird_fields():
            attr = self.get_moneybird_attr(field)
            result[field] = attr

        for field in self.get_moneybird_foreign_key_fields():  # Objects I have a foreign key to
            result[field] = self.get_moneybird_foreign_key_resource_data(field)

        for field in self.get_moneybird_nested_data_fields():  # Nested data objects that have a foreign key to me
            result[field + "_attributes"] = self.get_moneybird_nested_resource_data(field)

        return result

    def get_moneybird_nested_resource_data(self, field):
        """Get a Moneybird-API supported data representation of all nested objects."""
        if field in self.get_moneybird_nested_data_fields():
            nested_data = []
            for item in self.get_moneybird_attr(field).all():
                nested_data.append(item.get_moneybird_resource_data())
            return nested_data

    def get_moneybird_foreign_key_resource_data(self, field):
        """Get a Moneybird-API supported data representation of an object I have a foreign key to."""
        if field in self.get_moneybird_foreign_key_fields():
            return self.get_moneybird_attr(field).get_moneybird_resource_data()

    def set_moneybird_resource_data(self, data: Dict[str, Any]):
        """Update this object with data from the Moneybird API."""
        for field in data:

            if field in self.get_moneybird_foreign_key_fields():
                foreign_key_class = self._meta.get_field(field).remote_field.model
                if issubclass(foreign_key_class, MoneybirdSynchronizableResourceModel):
                    # If it is an independent object type, don't delete the current one
                    nested_data = data[field]
                    obj = foreign_key_class.update_or_create_object_from_moneybird(nested_data)
                    self.set_moneybird_attr(field, obj)
                elif issubclass(foreign_key_class, MoneybirdResourceModel):
                    nested_data = data[field]
                    current_obj = self.get_moneybird_attr(field)
                    if self.get_moneybird_attr(field).id != nested_data["id"]:
                        current_obj.processed = True
                        current_obj.delete()
                    obj = foreign_key_class.update_or_create_object_from_moneybird(nested_data)
                    self.set_moneybird_attr(field, obj)

            if field in self.get_moneybird_nested_data_fields():
                nested_data_class = self.get_moneybird_nested_data_fields()[field]
                if issubclass(nested_data_class, MoneybirdSynchronizableResourceModel):
                    pass  # Ignore independent object types, those will be synced independently
                elif issubclass(nested_data_class, MoneybirdNestedDataResourceModel):
                    nested_data = data[field]
                    if isinstance(
                        nested_data, list
                    ):  # Reversed foreign key are expected to be lists, as multiple can exist
                        current_objects = self.get_moneybird_attr(field).all()

                        to_delete = current_objects.exclude(id__in=[x["id"] for x in nested_data])
                        for delete_object in to_delete:
                            delete_object.processed = True
                            delete_object.delete()

                        new_objs = []
                        for obj_data in nested_data:
                            obj_data[nested_data_class.get_moneybird_nested_foreign_key() + "_id"] = self.id
                            obj = nested_data_class.update_or_create_object_from_moneybird(obj_data)
                            new_objs.append(obj)
                        # self.get_moneybird_attr(field).set(new_objs).save()  # technically this should not be required, as the reversed foreign key is already set

            if field in self.get_moneybird_fields():  # the default for simple fields
                self.set_moneybird_attr(field, data[field])

        return self

    @classmethod
    def update_or_create_object_from_moneybird(cls, data: Dict[str, Any]):
        obj = cls(id=data["id"]).set_moneybird_resource_data(data)
        obj.processed = True  # Prevent save() triggering a callback to Moneybird
        obj.save()
        return obj


class MoneybirdReadOnlyResourceModel(MoneybirdResourceModel):
    class Meta:
        abstract = True

    moneybird_resource_path_name = None

    @classmethod
    def get_moneybird_readonly_fields(cls):
        return cls.get_moneybird_fields()

    @classmethod
    def get_moneybird_resource_path_name(cls):
        if cls.moneybird_resource_path_name:
            return cls.moneybird_resource_path_name
        else:
            raise NotImplementedError


class MoneybirdReadWriteResourceModel(MoneybirdResourceModel):
    class Meta:
        abstract = True

    moneybird_resource_path_name = None

    @classmethod
    def get_moneybird_resource_path_name(cls):
        if cls.moneybird_resource_path_name:
            return cls.moneybird_resource_path_name
        else:
            raise NotImplementedError

    @property
    def moneybird_resource_url(self):
        return (
            f"https://moneybird.com/{settings.MONEYBIRD_ADMINISTRATION_ID}/{self.get_moneybird_resource_path_name()}/{self.id}/edit"
            if self.id
            else None
        )

    def get_absolute_url(self):
        return self.moneybird_resource_url


class MoneybirdSynchronizableResourceModel(MoneybirdReadWriteResourceModel):
    """
    Objects that can be synced with Moneybird resources.

    Those objects are expected to be reachable from the Moneybird API on their
    `moneybird_resource_path_name/synchronization` endpoint. The object's
    `id` and `version` are used to synchronize data with Moneybird.
    Attributes are expected to have names equal to those used in the Moneybird API,
    all other attributes are ignored on synchronization.

    For more details, check out https://developer.moneybird.com
    """

    class Meta:
        abstract = True

    version = models.IntegerField(
        null=True,
        blank=True,
        unique=True,
        help_text="This is the Moneybird version of the currently stored data and is used when looking for changes efficiently.",
    )

    @classmethod
    def get_moneybird_fields(cls):
        return super(MoneybirdSynchronizableResourceModel, cls).get_moneybird_fields() + ["version"]

    @classmethod
    def get_moneybird_readonly_fields(cls):
        return super(MoneybirdSynchronizableResourceModel, cls).get_moneybird_readonly_fields() + ["version"]

    @property
    def moneybird_resource_url(self):
        return (
            f"https://moneybird.com/{settings.MONEYBIRD_ADMINISTRATION_ID}/{self.get_moneybird_resource_path_name()}/{self.id}"
            if self.id
            else None
        )

    def get_absolute_url(self):
        return self.moneybird_resource_url


class MoneybirdNestedDataResourceModel(MoneybirdResourceModel):
    """Objects that dont exist independently but depend on another Model, like InvoiceDetailItems."""

    class Meta:
        abstract = True

    moneybird_nested_foreign_key = None  # Should also be in the moneybird_data_fields

    @classmethod
    def get_moneybird_nested_foreign_key(cls):
        return cls.moneybird_nested_foreign_key

    def get_moneybird_attr(self, field):
        if field == self.moneybird_nested_foreign_key:
            return getattr(self, field, None)
        return super(MoneybirdNestedDataResourceModel, self).get_moneybird_attr(field)

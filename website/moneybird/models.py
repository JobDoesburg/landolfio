from django.db import models
from django.db.models.utils import resolve_callables
from django.utils.translation import gettext as _

from moneybird.resource_types import get_moneybird_resource_for_model


class MoneybirdResourceModel(models.Model):
    moneybird_id = models.PositiveBigIntegerField(
        verbose_name=_("Moneybird ID"), null=True, blank=True
    )

    class Meta:
        abstract = True

    def save(self, push_to_moneybird=True, *args, **kwargs):
        if push_to_moneybird:
            resource_type_class = get_moneybird_resource_for_model(self.__class__)
            if resource_type_class is not None:

                if self.moneybird_id:
                    new_moneybird_data = resource_type_class.serialize_for_moneybird(
                        self
                    )
                    old_object = self.__class__.objects.get(id=self.id)
                    old_moneybird_data = resource_type_class.serialize_for_moneybird(
                        old_object
                    )
                    diff = dict(
                        set(old_moneybird_data.items())
                        ^ set(new_moneybird_data.items())
                    )
                    returned_data = resource_type_class.push_to_moneybird(self, diff)
                else:
                    returned_data = resource_type_class.push_to_moneybird(self)

                fields_to_update = resource_type_class.get_model_kwargs(returned_data)
                for k, v in resolve_callables(fields_to_update):
                    setattr(self, k, v)
                # TODO: also write / save document lines

        return super().save(*args, **kwargs)


class SynchronizableMoneybirdResourceModel(MoneybirdResourceModel):
    moneybird_version = models.PositiveBigIntegerField(
        verbose_name=_("Moneybird version"), null=True, blank=True
    )

    class Meta:
        abstract = True

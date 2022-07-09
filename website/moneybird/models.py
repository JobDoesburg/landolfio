from django.db import models, transaction
from django.db.models.utils import resolve_callables
from django.utils.translation import gettext as _

from moneybird.resource_types import get_moneybird_resource_for_model


class MoneybirdResourceQueryset(models.QuerySet):
    def create(self, push_to_moneybird=True, **kwargs):
        obj = self.model(**kwargs)
        self._for_write = True
        obj.save(push_to_moneybird=push_to_moneybird, force_insert=True, using=self.db)
        return obj

    def update_or_create(self, defaults=None, push_to_moneybird=True, **kwargs):
        defaults = defaults or {}
        self._for_write = True
        with transaction.atomic(using=self.db):
            # Lock the row so that a concurrent update is blocked until
            # update_or_create() has performed its save.
            obj, created = self.select_for_update().get_or_create(defaults, **kwargs)
            if created:
                return obj, created
            for k, v in resolve_callables(defaults):
                setattr(obj, k, v)
            obj.save(push_to_moneybird=push_to_moneybird, using=self.db)
        return obj, False


class MoneybirdResourceModelManager(models.Manager):
    _queryset_class = MoneybirdResourceQueryset


class MoneybirdResourceModel(models.Model):
    moneybird_id = models.PositiveBigIntegerField(
        verbose_name=_("Moneybird ID"), null=True, blank=True
    )

    objects = MoneybirdResourceModelManager()

    class Meta:
        abstract = True

    def save(self, push_to_moneybird=True, *args, **kwargs):
        # push_to_moneybird = kwargs.get('push_to_moneybird', True)

        if push_to_moneybird:
            resource_type_class = get_moneybird_resource_for_model(self.__class__)
            if resource_type_class is not None:
                returned_data = resource_type_class.push_to_moneybird(self)
                fields_to_update = resource_type_class.get_model_kwargs(returned_data)
                for attr, val in fields_to_update.items():
                    setattr(self, attr, val)
                # TODO: also write / save document lines

        return super().save(*args, **kwargs)


class SynchronizableMoneybirdResourceModel(MoneybirdResourceModel):
    moneybird_version = models.PositiveBigIntegerField(
        verbose_name=_("Moneybird version"), null=True, blank=True
    )

    class Meta:
        abstract = True

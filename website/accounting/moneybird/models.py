from django.db import models
from django.utils.translation import gettext as _


class MoneybirdResourceModel(models.Model):
    moneybird_id = models.PositiveBigIntegerField(
        verbose_name=_("Moneybird ID"), null=True, blank=True
    )

    class Meta:
        abstract = True


class SynchronizableMoneybirdResourceModel(MoneybirdResourceModel):
    moneybird_version = models.PositiveBigIntegerField(
        verbose_name=_("Moneybird version"), null=True, blank=True
    )

    class Meta:
        abstract = True

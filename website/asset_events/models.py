from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import PROTECT
from django.utils import timezone
from polymorphic.models import PolymorphicModel

from assets.models import Asset
from moneybird_accounting.models import Contact


class Event(PolymorphicModel):
    class Meta:
        verbose_name = "event"
        verbose_name_plural = "events"

    @classmethod
    def event_type(cls):
        return cls._meta.verbose_name

    asset = models.ForeignKey(Asset, null=False, blank=False, on_delete=PROTECT)
    memo = models.TextField(null=True, blank=True)

    def __str__(self):
        return f"{self.asset.number} {self.event_type()}"


class ConcreteAssetEvent(PolymorphicModel):
    class Meta:
        abstract = True

    created = models.DateTimeField(auto_now_add=True, blank=False, null=False)
    date = models.DateField(blank=False, null=False, default=timezone.now)


class StatusChangingEvent(Event):
    class Meta:
        abstract = True

    input_statuses = []
    output_status = None

    @classmethod
    def get_input_statuses(cls):
        return cls.input_statuses

    def get_output_status(self):
        return self.output_status

    def clean(self):
        super().clean()

        errors = {}
        try:
            if self.asset.status not in self.get_input_statuses() and False:  # TODO FIX THIS
                errors.update({"asset": f"Event cannot be added to asset with status {self.asset.status}."})
        except Asset.DoesNotExist:
            pass

        if errors:
            raise ValidationError(errors)

    def post_save(self):
        self.asset.status = self.get_output_status()
        self.asset.save()


class SingleStatusChangingEvent(StatusChangingEvent, ConcreteAssetEvent):
    def __str__(self):
        return f"{self.asset.number} {self.event_type()} ({self.date.strftime('%d-%m-%Y')})"


class MultiAssetEvent(ConcreteAssetEvent):
    pass


class MiscellaneousAssetEvent(SingleStatusChangingEvent):
    class Meta:
        verbose_name = "miscellaneous event"
        verbose_name_plural = "miscellaneous events"

    input_statuses = list(x for x, _ in Asset.STATUS_CHOICES)

    new_status = models.IntegerField(null=False, blank=False, choices=Asset.STATUS_CHOICES)

    def get_output_status(self):
        return self.new_status

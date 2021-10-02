from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import PROTECT
from django.utils import timezone
from model_utils import FieldTracker
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
    tracker = FieldTracker(['asset'])

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

        self.old_instance

        errors = {}
        try:
            if self.asset.status not in self.get_input_statuses() and False:  # TODO FIX THIS
                errors.update({"asset": f"Event cannot be added to asset with status {self.asset.status}."})
        except Asset.DoesNotExist:
            pass

        if errors:
            raise ValidationError(errors)

    def get_immutable_fields(self):
        immutable_fields = []
        if self is not self.asset.get_last_event():
            immutable_fields.append('asset')
        return immutable_fields

    def save(self, force_insert=False, force_update=False, using=None,
             update_fields=None):
        for field in self.get_immutable_fields():
            if self.tracker.has_changed(field) and (self.tracker.previous('field') is not None):
                raise ValidationError("This field is immutable.")
        super().save(force_insert, force_update, using, update_fields)



    def post_save(self):
        previous_asset = self.tracker.previous('asset')
        if previous_asset is not None and previous_asset != self.asset:
            previous_asset.status = previous_asset.tracker.previous('status')
            previous_asset.save()
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

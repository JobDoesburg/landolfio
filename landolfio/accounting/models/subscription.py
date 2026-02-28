from django.db import models
from django.utils.dateparse import parse_date
from django.utils.translation import gettext_lazy as _

from accounting.models.contact import Contact, ContactResourceType
from moneybird import resources
from moneybird.models import MoneybirdResourceModel
from moneybird.resource_types import MoneybirdResourceId


class Subscription(MoneybirdResourceModel):
    start_date = models.DateField(null=True, verbose_name=_("start date"))
    end_date = models.DateField(null=True, verbose_name=_("end date"))
    cancelled_at = models.DateField(null=True, verbose_name=_("cancelled at"))
    reference = models.CharField(
        verbose_name=_("reference"), max_length=255, null=False, blank=False
    )
    contact = models.ForeignKey(
        Contact,
        null=True,
        on_delete=models.SET_NULL,
        verbose_name=_("contact"),
        related_name="subscriptions",
    )

    def __str__(self):
        return f"{self.reference} {_('for')} {self.contact}"

    class Meta:
        verbose_name = _("subscription")
        verbose_name_plural = _("subscriptions")
        ordering = ("-start_date",)


class SubscriptionResourceType(resources.SubscriptionResourceType):
    model = Subscription

    @classmethod
    def get_model_kwargs(cls, resource_data):
        kwargs = super().get_model_kwargs(resource_data)
        kwargs["reference"] = resource_data["reference"]
        kwargs["start_date"] = (
            parse_date(resource_data["start_date"])
            if resource_data.get("start_date")
            else None
        )
        kwargs["end_date"] = (
            parse_date(resource_data["end_date"])
            if resource_data.get("end_date")
            else None
        )
        kwargs["cancelled_at"] = (
            parse_date(resource_data["cancelled_at"])
            if resource_data.get("cancelled_at")
            else None
        )
        kwargs["contact"] = ContactResourceType.get_or_create_from_moneybird_data(
            resource_data["contact_id"]
        )
        return kwargs

    @classmethod
    def serialize_for_moneybird(cls, instance):
        data = super().serialize_for_moneybird(instance)
        data["start_date"] = instance.start_date.isoformat()
        data["contact"] = MoneybirdResourceId(instance.contact.moneybird_id)
        if data.end_date:
            data["start_date"] = instance.end_date.isoformat()
        data["reference"] = instance.reference

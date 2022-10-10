from django.db import models
from django.utils.translation import gettext_lazy as _

from accounting.models.contact import Contact, ContactResourceType
from accounting.models.document_style import DocumentStyle
from accounting.models.product import Product, ProductResourceType
from accounting.models.recurring_sales_invoice import (
    RecurringSalesInvoiceFrequencies,
    RecurringSalesInvoice,
    RecurringSalesInvoiceResourceType,
)
from moneybird import resources
from moneybird.models import (
    MoneybirdResourceModel,
)
from moneybird.resource_types import MoneybirdResourceId


class Subscription(MoneybirdResourceModel):
    start_date = models.DateField(null=True, verbose_name=_("start date"))
    end_date = models.DateField(null=True, verbose_name=_("end date"))
    cancelled_at = models.DateField(null=True, verbose_name=_("cancelled at"))
    reference = models.CharField(
        verbose_name=_("reference"), max_length=255, null=False, blank=False
    )
    product = models.ForeignKey(
        Product,
        null=True,
        on_delete=models.SET_NULL,
        verbose_name=_("product"),
        related_name="subscription",
    )
    frequency = models.PositiveSmallIntegerField(
        default=1, verbose_name=_("frequency"), null=True, blank=True
    )
    frequency_type = models.CharField(
        max_length=10,
        choices=RecurringSalesInvoiceFrequencies.choices,
        verbose_name=_("frequency type"),
    )
    contact = models.ForeignKey(
        Contact,
        null=True,
        on_delete=models.SET_NULL,
        verbose_name=_("contact"),
        related_name="subscriptions",
    )
    recurring_sales_invoice = models.ForeignKey(
        RecurringSalesInvoice,
        null=True,
        on_delete=models.SET_NULL,
        verbose_name=_("recurring sales invoice"),
        related_name="subscriptions",
    )

    def __str__(self):
        return f"{self.product} {self.reference} {_('for')} {self.contact}"

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
        kwargs["start_date"] = resource_data["start_date"]
        kwargs["end_date"] = resource_data["end_date"]
        kwargs["cancelled_at"] = resource_data["cancelled_at"]
        kwargs["frequency"] = resource_data["frequency"]
        kwargs["frequency_type"] = resource_data["frequency_type"]
        kwargs["contact"] = ContactResourceType.get_or_create_from_moneybird_data(
            resource_data["contact_id"]
        )
        kwargs["product"] = ProductResourceType.get_or_create_from_moneybird_data(
            resource_data["product_id"]
        )
        kwargs[
            "recurring_sales_invoice"
        ] = RecurringSalesInvoiceResourceType.get_or_create_from_moneybird_data(
            resource_data["recurring_sales_invoice_id"],
        )
        return kwargs

    @classmethod
    def serialize_for_moneybird(cls, instance):
        data = super().serialize_for_moneybird(instance)
        data["start_date"] = instance.start_date.isoformat()
        data["product"] = MoneybirdResourceId(instance.product.moneybird_id)
        data["contact"] = MoneybirdResourceId(instance.contact.moneybird_id)
        if data.end_date:
            data["start_date"] = instance.end_date.isoformat()
        data["reference"] = instance.reference
        data["document_style_id"] = DocumentStyle.objects.get(default=True).moneybird_id
        data["frequency"] = instance.frequency
        data["frequency_type"] = instance.frequency_type

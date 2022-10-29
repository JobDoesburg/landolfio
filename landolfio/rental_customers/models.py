import logging

from django.db import models
from django.template import loader
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from accounting.models import Contact
from accounting.models.estimate import Estimate
from inventory.models.asset import Asset


class RegisteredRentalCustomer(models.Model):
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_("created at"))
    contact = models.ForeignKey(
        Contact,
        blank=False,
        null=True,
        on_delete=models.SET_NULL,
        verbose_name=_("contact"),
    )
    wants_sepa_mandate = models.BooleanField(
        default=True, verbose_name=_("Wants SEPA mandate")
    )
    sepa_mandate_sent = models.BooleanField(
        default=False, verbose_name=_("SEPA mandate request was sent")
    )
    wants_reduced_liability = models.BooleanField(
        default=True, verbose_name=_("Wants reduced liability")
    )
    affiliate_name = models.CharField(
        max_length=255, blank=True, null=True, verbose_name=_("affiliate name")
    )
    instrument_numbers = models.TextField(
        blank=True, verbose_name=_("instrument numbers")
    )
    rental_price = models.DecimalField(
        max_digits=6,
        decimal_places=2,
        blank=True,
        null=True,
        verbose_name=_("rental price"),
    )
    notes = models.TextField(blank=True, verbose_name=_("notes"))
    assets = models.ManyToManyField(verbose_name=_("assets"), to=Asset, blank=True)

    agreement = models.ForeignKey(
        Estimate,
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
        verbose_name=_("agreement"),
    )

    processed = models.BooleanField(default=False, verbose_name=_("Processed"))
    processed_at = models.DateTimeField(
        blank=True, null=True, verbose_name=_("processed at")
    )

    def __str__(self):
        return str(self.contact)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._processed = self.processed

    def save(
        self, force_insert=False, force_update=False, using=None, update_fields=None
    ):
        if self.processed and not self._processed:
            self._processed = True
            self.processed_at = timezone.now()

        if self.contact and not self.contact.is_synced_with_moneybird:
            self.contact.push_to_moneybird()

        if self.contact and self.wants_sepa_mandate and not self.sepa_mandate_sent:
            self.contact.request_payments_mandate(
                message=loader.render_to_string(
                    "email/mandate_request_message.txt", {"customer": self.contact}
                )
            )
            self.sepa_mandate_sent = True

        super().save(force_insert, force_update, using, update_fields)

    class Meta:
        verbose_name = _("registered rental customer")
        verbose_name_plural = _("registered rental customers")

from django.db import models
from django.utils.translation import gettext_lazy as _

from accounting.models import Contact
from accounting.models.estimate import Estimate
from inventory.models.asset import Asset
from new_customers.models import NewCustomer
from tickets.models import Ticket, TicketType

NEW_RENTAL_CUSTOMER_TICKET_TYPE = TicketType.objects.get_or_create(
    name="Nieuwe huurder", code_defined=True
)[0]


class NewRentalCustomer(NewCustomer):
    wants_reduced_liability = models.BooleanField(
        default=True, verbose_name=_("wants reduced liability")
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
    date_received = models.DateField(
        blank=True, null=True, verbose_name=_("date received")
    )

    def save(
        self, force_insert=False, force_update=False, using=None, update_fields=None
    ):
        if not self.ticket_type:
            self.ticket_type = NEW_RENTAL_CUSTOMER_TICKET_TYPE

        super().save(force_insert, force_update, using, update_fields)

    class Meta:
        verbose_name = _("new rental customer")
        verbose_name_plural = _("new rental customers")

from django.conf import settings
from django.db import models
from django.template import loader
from django.utils.translation import gettext_lazy as _

from moneybird.administration import MoneybirdNotConfiguredError
from tickets.models import Ticket, TicketType


def get_customer_ticket_type():
    return TicketType.objects.get_or_create(name="Nieuwe klant", code_defined=True)[0]


class NewCustomer(Ticket):
    wants_sepa_mandate = models.BooleanField(
        default=True, verbose_name=_("Wants SEPA mandate")
    )
    sepa_mandate_sent = models.BooleanField(
        default=False, verbose_name=_("SEPA mandate request was sent")
    )

    def save(
        self, force_insert=False, force_update=False, using=None, update_fields=None
    ):
        if not self.ticket_type:
            self.ticket_type = get_customer_ticket_type()

        try:
            if self.contact and not self.contact.is_synced_with_moneybird:
                self.contact.push_to_moneybird()

            if self.contact and self.wants_sepa_mandate and not self.sepa_mandate_sent:
                self.contact.request_payments_mandate(
                    message=loader.render_to_string(
                        "email/mandate_request_message.txt", {"customer": self.contact}
                    )
                )
                self.sepa_mandate_sent = True
        except MoneybirdNotConfiguredError as e:
            # Allow Moneybird to be disabled in development, treat it as if the mandate was sent
            if settings.DEBUG:
                self.sepa_mandate_sent = True
            else:
                raise e

        super().save(force_insert, force_update, using, update_fields)

    class Meta:
        verbose_name = _("new customer")
        verbose_name_plural = _("new customers")

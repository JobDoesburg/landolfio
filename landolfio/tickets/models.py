from django.contrib.auth import get_user_model
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from model_utils.managers import InheritanceManager

from accounting.models import GeneralJournalDocument, SalesInvoice
from accounting.models import Contact
from accounting.models import Estimate
from inventory.models.asset import Asset
from inventory.services import find_existing_asset_from_description


class TicketType(models.Model):
    name = models.CharField(max_length=255, verbose_name=_("name"))
    code_defined = models.BooleanField(default=False, verbose_name=_("code defined"))

    @classmethod
    def new_customer(cls):
        return cls.objects.get_or_create(name=_("New customer"), description="")[0]

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = _("ticket type")
        verbose_name_plural = _("ticket types")


class Ticket(models.Model):
    date_created = models.DateTimeField(verbose_name=_("created at"), auto_now_add=True)
    date_updated = models.DateTimeField(verbose_name=_("updated at"), auto_now=True)
    closed = models.BooleanField(verbose_name=_("closed"), default=False)
    date_closed = models.DateTimeField(
        verbose_name=_("closed at"), null=True, blank=True
    )
    date_due = models.DateField(verbose_name=_("date due"), null=True, blank=True)

    created_by = models.ForeignKey(
        get_user_model(),
        verbose_name=_("created by"),
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="tickets_created",
    )
    assigned_to = models.ForeignKey(
        get_user_model(),
        verbose_name=_("assigned to"),
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="tickets_assigned",
    )

    ticket_type = models.ForeignKey(
        TicketType,
        on_delete=models.SET_NULL,
        null=True,
        blank=False,
        verbose_name=_("ticket type"),
    )
    title = models.CharField(
        max_length=255, verbose_name=_("title"), blank=True, null=True
    )
    description = models.TextField(verbose_name=_("description"), blank=True, null=True)

    assets = models.ManyToManyField(
        Asset, verbose_name=_("assets"), blank=True, related_name="tickets"
    )
    contact = models.ForeignKey(
        Contact,
        verbose_name=_("contact"),
        on_delete=models.PROTECT,
        blank=True,
        null=True,
        related_name="tickets",
    )
    estimates = models.ManyToManyField(
        Estimate, verbose_name=_("estimate"), blank=True, related_name="tickets"
    )
    sales_invoices = models.ManyToManyField(
        SalesInvoice,
        verbose_name=_("sales invoices"),
        blank=True,
        related_name="tickets",
    )

    objects = InheritanceManager()

    def __str__(self):
        return _("Ticket") + f" #{self.id} {self.title or ''}"

    def save(self, *args, **kwargs):
        if self.closed and not self.date_closed:
            # If the ticket is closed and the date_closed is not set, set it to now
            self.date_closed = timezone.now()

        if self.assets.count() == 0 and not self.closed:
            # If the ticket has no assets, try to find them from the description, but do not overwrite existing assets
            detected_assets = find_existing_asset_from_description(self.description)
            self.assets.set(detected_assets, clear=True)

        super().save(*args, **kwargs)

    def close(self):
        self.closed = True
        self.save()

    def reopen(self):
        self.closed = False
        self.date_closed = None
        self.save()

    class Meta:
        verbose_name = _("ticket")
        verbose_name_plural = _("tickets")

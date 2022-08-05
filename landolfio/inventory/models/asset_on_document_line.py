from django.db import models
from django.utils.translation import gettext_lazy as _

from accounting.models import (
    JournalDocumentLine,
    Subscription,
    RecurringSalesInvoiceDocumentLine,
)
from accounting.models.estimate import (
    EstimateDocumentLine,
)


class AssetOnJournalDocumentLine(models.Model):
    asset = models.ForeignKey(
        "Asset",
        on_delete=models.CASCADE,
        related_name="journal_document_line_assets",
        verbose_name=_("asset"),
    )
    document_line = models.ForeignKey(
        JournalDocumentLine,
        on_delete=models.CASCADE,
        related_name="assets",
        verbose_name=_("document line"),
    )
    value = models.DecimalField(
        max_digits=10, decimal_places=2, verbose_name=_("value")
    )

    @property
    def date(self):
        return self.document_line.date

    @property
    def contact(self):
        return self.document_line.contact

    @property
    def ledger_account(self):
        return self.document_line.ledger_account

    @property
    def description(self):
        return self.document_line.description

    @property
    def document(self):
        return self.document_line.document

    # TODO add a `aandeel in geheel` field here and determine value based on that

    class Meta:
        verbose_name = _("asset on journal document line")
        verbose_name_plural = _("assets on journal document lines")
        unique_together = [
            ("asset", "document_line"),
        ]

    def __str__(self):
        return f"{self.asset} {_('on')} {self.document_line} [{self.value}]"


class AssetOnEstimateDocumentLine(models.Model):
    asset = models.ForeignKey(
        "Asset",
        on_delete=models.CASCADE,
        related_name="estimate_document_line_assets",
        verbose_name=_("asset"),
    )
    document_line = models.ForeignKey(
        EstimateDocumentLine,
        on_delete=models.CASCADE,
        related_name="assets",
        verbose_name=_("document line"),
    )
    value = models.DecimalField(
        max_digits=10, decimal_places=2, verbose_name=_("value")
    )

    @property
    def date(self):
        return self.document_line.date

    @property
    def contact(self):
        return self.document_line.contact

    @property
    def ledger_account(self):
        return self.document_line.ledger_account

    @property
    def description(self):
        return self.document_line.description

    @property
    def document(self):
        return self.document_line.document

    class Meta:
        verbose_name = _("asset on estimate document line")
        verbose_name_plural = _("assets on estimate document lines")
        unique_together = [
            ("asset", "document_line"),
        ]

    def __str__(self):
        return f"{self.asset} {_('on')} {self.document_line} [{self.value}]"


class AssetOnRecurringSalesInvoiceDocumentLine(models.Model):
    asset = models.ForeignKey(
        "Asset",
        on_delete=models.CASCADE,
        related_name="recurring_sales_invoice_document_line_assets",
        verbose_name=_("asset"),
    )
    document_line = models.ForeignKey(
        RecurringSalesInvoiceDocumentLine,
        on_delete=models.CASCADE,
        related_name="assets",
        verbose_name=_("document line"),
    )
    value = models.DecimalField(
        max_digits=10, decimal_places=2, verbose_name=_("value")
    )

    @property
    def date(self):
        return self.document_line.date

    @property
    def contact(self):
        return self.document_line.contact

    @property
    def ledger_account(self):
        return self.document_line.ledger_account

    @property
    def description(self):
        return self.document_line.description

    @property
    def document(self):
        return self.document_line.document

    class Meta:
        verbose_name = _("asset on recurring sales invoice document line")
        verbose_name_plural = _("assets on recurring sales invoice document lines")
        unique_together = [
            ("asset", "document_line"),
        ]

    def __str__(self):
        return f"{self.asset} {_('on')} {self.document_line} [{self.value}]"


class AssetSubscription(models.Model):
    asset = models.ForeignKey(
        "Asset",
        on_delete=models.CASCADE,
        related_name="asset_subscriptions",
        verbose_name=_("asset"),
    )
    subscription = models.ForeignKey(
        Subscription,
        on_delete=models.CASCADE,
        related_name="assets",
        verbose_name=_("subscription"),
    )
    value = models.DecimalField(
        max_digits=10, decimal_places=2, verbose_name=_("value")
    )

    class Meta:
        verbose_name = _("asset subscription")
        verbose_name_plural = _("assets subscriptions")
        unique_together = [
            ("asset", "subscription"),
        ]

    def __str__(self):
        return f"{self.asset} {_('on')} {self.subscription} [{self.value}]"

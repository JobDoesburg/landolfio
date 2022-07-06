from django.db import models
from django.utils.translation import gettext as _

from accounting.moneybird.models import (
    MoneybirdResourceModel,
    SynchronizableMoneybirdResourceModel,
)


class Contact(SynchronizableMoneybirdResourceModel):
    moneybird_json = models.JSONField(verbose_name=_("JSON MoneyBird"), null=True)
    company_name = models.CharField(
        verbose_name=_("company name"),
        max_length=100,
        null=True,
        blank=True,
    )
    first_name = models.CharField(
        verbose_name=_("first name"),
        max_length=100,
        null=True,
        blank=True,
    )
    last_name = models.CharField(
        verbose_name=_("last name"),
        max_length=100,
        null=True,
        blank=True,
    )
    email = models.EmailField(
        verbose_name=_("email"),
        null=True,
        blank=True,
    )
    sepa_active = models.BooleanField(verbose_name=_("sepa active"), default=False)

    def __str__(self):
        if self.company_name:
            return self.company_name
        return f"{self.first_name} {self.last_name}"


class LedgerKind(models.TextChoices):
    VOORRAAD_MARGE = "VOORRAAD_MARGE", "Voorraad Marge"
    VOORRAAD_NIET_MARGE = "VOORRAAD_NIET_MARGE", "Voorraad niet-marge"
    VOORRAAD_BIJ_VERKOOP_MARGE = (
        "VOORRAAD_BIJ_VERKOOP_MARGE",
        "Voorraadwaarde bij verkoop marge",
    )
    VOORRAAD_BIJ_VERKOOP_NIET_MARGE = (
        "VOORRAAD_BIJ_VERKOOP_NIET_MARGE",
        "Voorraadwaarde bij verkoop niet-marge",
    )
    VERKOOP_MARGE = "VERKOOP_MARGE", "Verkoop marge"
    VERKOOP_NIET_MARGE = "VERKOOP_NIET_MARGE", "Verkoop niet-marge"
    DIRECTE_AFSCHRIJVING = "DIRECTE_AFSCHRIJVING", "Directe afschrijving"
    AFSCHRIJVINGEN = "AFSCHRIJVINGEN", "Afschrijvingen"
    BORGEN = "BORGEN", "Borgen"


class LedgerAccountType(models.TextChoices):
    NON_CURRENT_ASSETS = "non_current_assets", _("non current assets")
    CURRENT_ASSETS = "current_assets", _("current assets")
    EQUITY = "equity", _("equity")
    PROVISIONS = "provisions", _("provisions")
    NON_CURRENT_LIABILITIES = "non_current_liabilities", _("non current liabilities")
    CURRENT_LIABILITIES = "current_liabilities", _("current liabilities")
    REVENUE = "revenue", _("revenue")
    DIRECT_COSTS = "direct_costs", _("direct costs")
    EXPENSES = "expenses", _("expenses")
    OTHER_INCOME_EXPENSES = "other_income_expenses", _("other income expenses")


class Ledger(MoneybirdResourceModel):
    name = models.CharField(
        max_length=100,
        null=True,
        blank=True,
    )

    account_type = models.CharField(
        max_length=100,
        choices=LedgerAccountType.choices,
        null=True,
        verbose_name=_("Account type"),
    )

    ledger_kind = models.CharField(
        max_length=100,
        choices=LedgerKind.choices,
        null=True,
        unique=True,
        verbose_name=_("Kind"),
    )

    class Meta:
        verbose_name = _("Ledger account")
        verbose_name_plural = _("Ledger accounts")

    def __str__(self):
        if self.name:
            return self.name
        if not self.ledger_kind:
            return str(self.moneybird_id)
        return LedgerKind(self.ledger_kind).label


class DocumentKind(models.TextChoices):
    SALES_INVOICE = "FAC", _("Sales invoice")
    PURCHASE_INVOICE = "INK", _("Purchase invoice")
    RECEIPT = "BON", _("Receipt")
    GENERAL_JOURNAL_DOCUMENT = "MEM", _("General journal document")


class JournalDocument(SynchronizableMoneybirdResourceModel):
    date = models.DateField(null=True, verbose_name=_("Date"))
    moneybird_json = models.JSONField(verbose_name=_("JSON MoneyBird"), null=True)
    document_kind = models.CharField(
        max_length=3, choices=DocumentKind.choices, verbose_name=_("document kind")
    )
    contact = models.ForeignKey(
        Contact,
        null=True,
        on_delete=models.SET_NULL,
        verbose_name=_("Contact"),
        related_name="journal_documents",
    )

    def __str__(self):
        if self.document_kind == DocumentKind.SALES_INVOICE:
            if self.moneybird_json["invoice_id"] is not None:
                return f"{self.document_kind} {self.moneybird_json['invoice_id']}"
            return (
                f"{self.document_kind} {_('draft')} {self.moneybird_json['draft_id']}"
            )
        else:
            return f"{self.document_kind} {self.moneybird_json['reference']}"

    class Meta:
        unique_together = ("moneybird_id", "document_kind")
        verbose_name = _("Journal document")
        verbose_name_plural = _("Journal documents")
        ordering = ("-date",)


class JournalDocumentLine(MoneybirdResourceModel):
    moneybird_json = models.JSONField(verbose_name=_("JSON MoneyBird"), null=True)
    ledger = models.ForeignKey(
        Ledger, on_delete=models.PROTECT, verbose_name=_("Ledger")
    )
    price = models.DecimalField(
        max_digits=19, decimal_places=4, verbose_name=_("Price")
    )
    document = models.ForeignKey(
        JournalDocument,
        on_delete=models.CASCADE,
        verbose_name=_("Document"),
        related_name="document_lines",
    )
    asset_id_field = models.CharField(
        max_length=50, null=True, verbose_name=_("Asset Id")
    )
    asset = models.ForeignKey(
        "inventory.Asset",
        null=True,
        on_delete=models.SET_NULL,
        verbose_name=_("Asset"),
        related_name="document_lines",
    )

    def __str__(self):
        return f"Line in {self.document} with asset {self.asset_id}"

    class Meta:
        verbose_name = _("Journal document line")
        verbose_name_plural = _("Journal document lines")
        ordering = ("-document__date",)


class Estimate(SynchronizableMoneybirdResourceModel):
    moneybird_json = models.JSONField(verbose_name=_("JSON MoneyBird"), null=True)
    date = models.DateField(null=True, verbose_name=_("Date"))
    contact = models.ForeignKey(
        Contact,
        null=True,
        on_delete=models.SET_NULL,
        verbose_name=_("Contact"),
        related_name="estimates",
    )

    def __str__(self):
        if self.moneybird_json["estimate_id"] is not None:
            return f"OFF {self.moneybird_json['estimate_id']}"
        return f"OFF {_('draft')} {self.moneybird_json['draft_id']}"

    class Meta:
        verbose_name = _("Estimate")
        verbose_name_plural = _("Estimates")
        ordering = ("-date",)


class EstimateDocumentLine(MoneybirdResourceModel):
    moneybird_json = models.JSONField(verbose_name=_("JSON MoneyBird"), null=True)
    document = models.ForeignKey(
        Estimate,
        on_delete=models.CASCADE,
        verbose_name=_("Document"),
        related_name="document_lines",
    )
    asset_id_field = models.CharField(
        max_length=50, null=True, verbose_name=_("Asset Id")
    )
    asset = models.ForeignKey(
        "inventory.Asset",
        null=True,
        on_delete=models.SET_NULL,
        verbose_name=_("Asset"),
        related_name="estimate_document_lines",
    )

    def __str__(self):
        return f"Line in {self.document} with asset {self.asset_id}"

    class Meta:
        verbose_name = _("Estimate document line")
        verbose_name_plural = _("Estimate document lines")
        ordering = ("-document__date",)


class RecurringSalesInvoiceFrequencies(models.TextChoices):
    DAY = "day", _("day")
    WEEK = "week", _("week")
    MONTH = "month", _("month")
    QUARTER = "quarter", _("quarter")
    YEAR = "year", _("year")


class RecurringSalesInvoice(SynchronizableMoneybirdResourceModel):
    moneybird_json = models.JSONField(verbose_name=_("JSON MoneyBird"), null=True)
    contact = models.ForeignKey(
        Contact,
        null=True,
        on_delete=models.SET_NULL,
        verbose_name=_("Contact"),
        related_name="recurring_sales_invoices",
    )
    auto_send = models.BooleanField(verbose_name=_("Auto send"))
    active = models.BooleanField(verbose_name=_("Active"))
    frequency = models.CharField(
        max_length=10,
        choices=RecurringSalesInvoiceFrequencies.choices,
        verbose_name=_("frequency"),
    )
    start_date = models.DateField(null=True, verbose_name=_("start date"))
    invoice_date = models.DateField(null=True, verbose_name=_("invoice date"))
    last_date = models.DateField(null=True, verbose_name=_("last date"))

    def __str__(self):
        return f"PER {self.contact} every {self.frequency} since {self.start_date}"

    class Meta:
        verbose_name = _("Recurring sales invoice")
        verbose_name_plural = _("Recurring sales invoices")
        ordering = ("-start_date",)


class RecurringSalesInvoiceDocumentLine(MoneybirdResourceModel):
    moneybird_json = models.JSONField(verbose_name=_("JSON MoneyBird"), null=True)
    document = models.ForeignKey(
        RecurringSalesInvoice,
        on_delete=models.CASCADE,
        verbose_name=_("Document"),
        related_name="document_lines",
    )
    asset_id_field = models.CharField(
        max_length=50, null=True, verbose_name=_("Asset Id")
    )
    asset = models.ForeignKey(
        "inventory.Asset",
        null=True,
        on_delete=models.SET_NULL,
        verbose_name=_("Asset"),
        related_name="recurring_sales_invoice_document_lines",
    )

    def __str__(self):
        return f"Line in {self.document} with asset {self.asset_id}"

    class Meta:
        verbose_name = _("Recurring sales invoice document line")
        verbose_name_plural = _("Recurring sales invoice document lines")
        ordering = ("-document__start_date",)


class Subscription(MoneybirdResourceModel):
    moneybird_json = models.JSONField(verbose_name=_("JSON MoneyBird"), null=True)


class Product(MoneybirdResourceModel):
    moneybird_json = models.JSONField(verbose_name=_("JSON MoneyBird"), null=True)

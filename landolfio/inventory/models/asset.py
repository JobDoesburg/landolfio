from decimal import Decimal

from django.db import models
from django.db.models import (
    PROTECT,
    Sum,
    Count,
    Q,
    F,
)
from django.db.models.functions import Coalesce
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from queryable_properties.managers import QueryablePropertiesManager
from queryable_properties.properties import (
    RelatedExistenceCheckProperty,
    AggregateProperty,
    AnnotationProperty,
    ValueCheckProperty,
)

from accounting.models import (
    JournalDocumentLine,
    RecurringSalesInvoiceDocumentLine,
)
from accounting.models.ledger_account import LedgerAccountType, LedgerAccount
from accounting.models.estimate import (
    EstimateStates,
    EstimateDocumentLine,
)
from inventory.models.asset_on_document_line import (
    AssetOnJournalDocumentLine,
    AssetOnEstimateDocumentLine,
    AssetOnRecurringSalesInvoiceDocumentLine,
)
from inventory.models.category import AssetCategory, AssetSize
from inventory.models.collection import Collection
from inventory.models.location import AssetLocation


class FilteredRelatedExistenceCheckProperty(RelatedExistenceCheckProperty):
    def __init__(self, check_property, filter=None, *args, **kwargs):
        super().__init__(check_property, *args, **kwargs)
        self.filter = filter

    def get_queryset(self, model):
        return super().get_queryset(model).filter(self.filter)


class AssetStates(models.TextChoices):
    UNKNOWN = "unknown", _("unknown")
    PLACEHOLDER = "placeholder", _("placeholder")
    TO_BE_DELIVERED = "to_be_delivered", _("to be delivered")
    UNDER_REVIEW = "under_review", _("under review")
    MAINTENANCE_IN_HOUSE = "maintenance_in_house", _("maintenance in house")
    MAINTENANCE_EXTERNAL = "maintenance_external", _("maintenance external")
    AVAILABLE = "available", _("available")
    ISSUED_UNPROCESSED = "issued_unprocessed", _("issued unprocessed")
    ISSUED_RENT = "issued_rent", _("issued rent")
    ISSUED_LOAN = "issued_loan", _("issued loan")
    AMORTIZED = "amortized", _("amortized")
    SOLD = "sold", _("sold")


class AccountingStates(models.TextChoices):
    UNKNOWN = "unknown", _("unknown")  # does not occur in the accounting system
    AVAILABLE = "available", _("available")  # purchased, not amortized, not sold
    AVAILABLE_OR_AMORTIZED = "available_or_amortized", _(
        "available or amortized"
    )  # amortized at purchase
    ISSUED_RENT = "issued_rent", _("issued rent")
    ISSUED_LOAN = "issued_loan", _("issued loan")
    AMORTIZED = "amortized", _("amortized")
    SOLD = "sold", _("sold")


class Asset(models.Model):
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_("created at"))
    id = models.CharField(verbose_name=_("ID"), max_length=200, primary_key=True)
    category = models.ForeignKey(
        AssetCategory,
        null=True,
        blank=False,
        on_delete=PROTECT,
        verbose_name=_("category"),
    )
    size = models.ForeignKey(
        AssetSize, null=True, blank=True, on_delete=PROTECT, verbose_name=_("size")
    )
    location = models.ForeignKey(
        AssetLocation,
        null=True,
        blank=True,
        on_delete=PROTECT,
        verbose_name=_("location"),
    )
    collection = models.ForeignKey(
        Collection, on_delete=models.CASCADE, verbose_name=_("collection")
    )

    listing_price = models.DecimalField(
        verbose_name=_("listing price"),
        null=True,
        blank=True,
        max_digits=10,
        decimal_places=2,
    )
    local_status = models.CharField(
        max_length=40,
        choices=AssetStates.choices,
        verbose_name=_("local status"),
        default=AssetStates.UNKNOWN,
    )

    journal_document_lines = models.ManyToManyField(
        JournalDocumentLine,
        through=AssetOnJournalDocumentLine,
        verbose_name=_("journal document lines"),
    )
    estimate_document_lines = models.ManyToManyField(
        EstimateDocumentLine,
        through=AssetOnEstimateDocumentLine,
        verbose_name=_("estimate document lines"),
    )
    recurring_sales_invoice_document_lines = models.ManyToManyField(
        RecurringSalesInvoiceDocumentLine,
        through=AssetOnRecurringSalesInvoiceDocumentLine,
        verbose_name=_("recurring sales invoice document lines"),
    )

    raw_data = models.JSONField(verbose_name=_("raw data"), null=True, blank=True)

    @property
    def get_ledger_account_amounts(self):
        return dict(
            (
                LedgerAccount.objects.get(
                    moneybird_id=x["document_line__ledger_account__moneybird_id"]
                ),
                x["value__sum"],
            )
            for x in self.journal_document_line_assets.values(
                "document_line__ledger_account__moneybird_id"
            ).annotate(Sum("value"))
        )

    @property
    def get_balance_ledger_account_amounts(self):
        return dict(
            filter(
                lambda x: x[0].is_balance,
                self.get_ledger_account_amounts.items(),
            )
        )

    @property
    def get_results_ledger_account_amounts(self):
        return dict(
            filter(
                lambda x: x[0].is_results,
                self.get_ledger_account_amounts.items(),
            )
        )

    total_assets_value = AggregateProperty(
        Sum(
            "journal_document_line_assets__value",
            filter=Q(
                journal_document_line_assets__document_line__ledger_account__account_type=LedgerAccountType.CURRENT_ASSETS
            ),
            output_field=models.DecimalField(max_digits=10, decimal_places=2),
        ),
    )
    total_margin_assets_value = AggregateProperty(
        Sum(
            "journal_document_line_assets__value",
            filter=Q(
                journal_document_line_assets__document_line__ledger_account__account_type=LedgerAccountType.CURRENT_ASSETS,
                journal_document_line_assets__document_line__ledger_account__is_margin=True,
            ),
            output_field=models.DecimalField(max_digits=10, decimal_places=2),
        )
    )
    total_non_margin_assets_value = AggregateProperty(
        Sum(
            "journal_document_line_assets__value",
            filter=Q(
                journal_document_line_assets__document_line__ledger_account__account_type=LedgerAccountType.CURRENT_ASSETS,
                journal_document_line_assets__document_line__ledger_account__is_margin=False,
            ),
            output_field=models.DecimalField(max_digits=10, decimal_places=2),
        )
    )

    total_direct_costs_value = AggregateProperty(
        Sum(
            "journal_document_line_assets__value",
            filter=Q(
                journal_document_line_assets__document_line__ledger_account__account_type=LedgerAccountType.DIRECT_COSTS
            ),
            output_field=models.DecimalField(max_digits=10, decimal_places=2),
        )
    )
    total_margin_direct_costs_value = AggregateProperty(
        Sum(
            "journal_document_line_assets__value",
            filter=Q(
                journal_document_line_assets__document_line__ledger_account__account_type=LedgerAccountType.DIRECT_COSTS,
                journal_document_line_assets__document_line__ledger_account__is_margin=True,
            ),
            output_field=models.DecimalField(max_digits=10, decimal_places=2),
        )
    )
    total_non_margin_direct_costs_value = AggregateProperty(
        Sum(
            "journal_document_line_assets__value",
            filter=Q(
                journal_document_line_assets__document_line__ledger_account__account_type=LedgerAccountType.DIRECT_COSTS,
                journal_document_line_assets__document_line__ledger_account__is_margin=False,
            ),
            output_field=models.DecimalField(max_digits=10, decimal_places=2),
        )
    )

    total_expenses_value = AggregateProperty(
        Sum(
            "journal_document_line_assets__value",
            filter=Q(
                journal_document_line_assets__document_line__ledger_account__account_type=LedgerAccountType.EXPENSES
            ),
            output_field=models.DecimalField(max_digits=10, decimal_places=2),
        )
    )
    total_purchase_expenses = AggregateProperty(
        Sum(
            "journal_document_line_assets__value",
            filter=Q(
                journal_document_line_assets__document_line__ledger_account__account_type=LedgerAccountType.EXPENSES,
                journal_document_line_assets__document_line__ledger_account__is_purchase=True,
            ),
            output_field=models.DecimalField(max_digits=10, decimal_places=2),
        )
    )
    total_other_expenses = AggregateProperty(
        Sum(
            "journal_document_line_assets__value",
            filter=Q(
                journal_document_line_assets__document_line__ledger_account__account_type=LedgerAccountType.EXPENSES,
                journal_document_line_assets__document_line__ledger_account__is_purchase=False,
            ),
            output_field=models.DecimalField(max_digits=10, decimal_places=2),
        )
    )

    total_revenue_value = AggregateProperty(
        Sum(
            "journal_document_line_assets__value",
            filter=Q(
                journal_document_line_assets__document_line__ledger_account__account_type=LedgerAccountType.REVENUE
            ),
            output_field=models.DecimalField(max_digits=10, decimal_places=2),
        )
    )
    total_sales_revenue = AggregateProperty(
        Sum(
            "journal_document_line_assets__value",
            filter=Q(
                journal_document_line_assets__document_line__ledger_account__account_type=LedgerAccountType.REVENUE,
                journal_document_line_assets__document_line__ledger_account__is_sales=True,
            ),
            output_field=models.DecimalField(max_digits=10, decimal_places=2),
        )
    )
    total_sales_revenue_margin = AggregateProperty(
        Sum(
            "journal_document_line_assets__value",
            filter=Q(
                journal_document_line_assets__document_line__ledger_account__account_type=LedgerAccountType.REVENUE,
                journal_document_line_assets__document_line__ledger_account__is_sales=True,
                journal_document_line_assets__document_line__ledger_account__is_margin=True,
            ),
            output_field=models.DecimalField(max_digits=10, decimal_places=2),
        )
    )
    total_sales_revenue_non_margin = AggregateProperty(
        Sum(
            "journal_document_line_assets__value",
            filter=Q(
                journal_document_line_assets__document_line__ledger_account__account_type=LedgerAccountType.REVENUE,
                journal_document_line_assets__document_line__ledger_account__is_sales=True,
                journal_document_line_assets__document_line__ledger_account__is_margin=False,
            ),
            output_field=models.DecimalField(max_digits=10, decimal_places=2),
        )
    )
    total_other_revenue = AggregateProperty(
        Sum(
            "journal_document_line_assets__value",
            filter=Q(
                journal_document_line_assets__document_line__ledger_account__account_type=LedgerAccountType.REVENUE,
                journal_document_line_assets__document_line__ledger_account__is_sales=False,
            ),
            output_field=models.DecimalField(max_digits=10, decimal_places=2),
        )
    )

    is_margin = FilteredRelatedExistenceCheckProperty(
        "journal_document_lines",
        filter=Q(
            Q(
                journal_document_line_assets__document_line__ledger_account__is_margin=True
            ),
            Q(
                Q(
                    journal_document_line_assets__document_line__ledger_account__is_sales=True
                )
                | Q(
                    journal_document_line_assets__document_line__ledger_account__is_purchase=True
                )
                | Q(
                    journal_document_line_assets__document_line__ledger_account__is_assets_inventory=True
                )
            ),
        ),
    )
    is_non_margin = FilteredRelatedExistenceCheckProperty(
        "journal_document_lines",
        filter=Q(
            Q(
                journal_document_line_assets__document_line__ledger_account__is_margin=False
            ),
            Q(
                Q(
                    journal_document_line_assets__document_line__ledger_account__is_sales=True
                )
                | Q(
                    journal_document_line_assets__document_line__ledger_account__is_purchase=True
                )
                | Q(
                    journal_document_line_assets__document_line__ledger_account__is_assets_inventory=True
                )
            ),
        ),
    )

    is_sold = FilteredRelatedExistenceCheckProperty(
        "journal_document_lines",
        filter=Q(
            journal_document_line_assets__document_line__ledger_account__account_type=LedgerAccountType.REVENUE,
            journal_document_line_assets__document_line__ledger_account__is_sales=True,
        ),
    )
    is_sold_as_margin = FilteredRelatedExistenceCheckProperty(
        "journal_document_lines",
        filter=Q(
            journal_document_line_assets__document_line__ledger_account__account_type=LedgerAccountType.REVENUE,
            journal_document_line_assets__document_line__ledger_account__is_sales=True,
            journal_document_line_assets__document_line__ledger_account__is_margin=True,
        ),
    )
    is_sold_as_non_margin = FilteredRelatedExistenceCheckProperty(
        "journal_document_lines",
        filter=Q(
            journal_document_line_assets__document_line__ledger_account__account_type=LedgerAccountType.REVENUE,
            journal_document_line_assets__document_line__ledger_account__is_sales=True,
            journal_document_line_assets__document_line__ledger_account__is_margin=False,
        ),
    )

    is_purchased_asset = FilteredRelatedExistenceCheckProperty(
        "journal_document_lines",
        filter=Q(
            journal_document_line_assets__document_line__ledger_account__account_type=LedgerAccountType.CURRENT_ASSETS
        ),
    )
    is_purchased_asset_as_margin = FilteredRelatedExistenceCheckProperty(
        "journal_document_lines",
        filter=Q(
            journal_document_line_assets__document_line__ledger_account__account_type=LedgerAccountType.CURRENT_ASSETS,
            journal_document_line_assets__document_line__ledger_account__is_margin=True,
        ),
    )
    is_purchased_asset_as_non_margin = FilteredRelatedExistenceCheckProperty(
        "journal_document_lines",
        filter=Q(
            journal_document_line_assets__document_line__ledger_account__account_type=LedgerAccountType.CURRENT_ASSETS,
            journal_document_line_assets__document_line__ledger_account__is_margin=False,
        ),
    )

    is_purchased_amortized = FilteredRelatedExistenceCheckProperty(
        "journal_document_lines",
        filter=Q(
            journal_document_line_assets__document_line__ledger_account__account_type=LedgerAccountType.EXPENSES,
            journal_document_line_assets__document_line__ledger_account__is_purchase=True,
        ),
    )

    purchase_value = AnnotationProperty(
        Coalesce(F("total_assets_value"), Decimal(0))
        + Coalesce(F("total_direct_costs_value"), Decimal(0))
        + Coalesce(F("total_purchase_expenses"), Decimal(0))
    )

    sales_profit = AnnotationProperty(
        Coalesce(F("total_sales_revenue"), Decimal(0))
        - Coalesce(F("purchase_value"), Decimal(0))
    )

    total_profit = AnnotationProperty(
        Coalesce(F("total_revenue_value"), Decimal(0))
        - Coalesce(F("total_direct_costs_value"), Decimal(0))
        - Coalesce(F("total_expenses_value"), Decimal(0))
    )

    coalesce_total_assets_value = AnnotationProperty(
        Coalesce(F("total_assets_value"), Decimal(0))
    )

    is_amortized = ValueCheckProperty("coalesce_total_assets_value", Decimal(0))

    is_commerce = FilteredRelatedExistenceCheckProperty(
        "collection", filter=Q(collection__commerce=True)
    )

    is_rented = FilteredRelatedExistenceCheckProperty(
        "recurring_sales_invoice_document_lines",
        filter=Q(
            recurring_sales_invoice_document_lines__document__active=True,
        ),
    )

    has_rental_agreement = FilteredRelatedExistenceCheckProperty(
        "estimate_document_lines",
        filter=Q(
            estimate_document_lines__document__state__in=[
                EstimateStates.OPEN,
                EstimateStates.LATE,
                EstimateStates.ACCEPTED,
            ],
            estimate_document_lines__document__workflow__is_rental=True,
        ),
    )
    num_rental_agreements = AggregateProperty(
        Count(
            "estimate_document_lines",
            filter=Q(
                estimate_document_lines__document__state__in=[
                    EstimateStates.OPEN,
                    EstimateStates.LATE,
                    EstimateStates.ACCEPTED,
                ],
                estimate_document_lines__document__workflow__is_rental=True,
            ),
        )
    )

    has_loan_agreement = FilteredRelatedExistenceCheckProperty(
        "estimate_document_lines",
        filter=Q(
            estimate_document_lines__document__state__in=[
                EstimateStates.OPEN,
                EstimateStates.LATE,
                EstimateStates.ACCEPTED,
            ],
            estimate_document_lines__document__workflow__is_loan=True,
        ),
    )

    num_loan_agreements = AggregateProperty(
        Count(
            "estimate_document_lines",
            filter=Q(
                estimate_document_lines__document__state__in=[
                    EstimateStates.OPEN,
                    EstimateStates.LATE,
                    EstimateStates.ACCEPTED,
                ],
                estimate_document_lines__document__workflow__is_loan=True,
            ),
        )
    )

    attachment_count = AggregateProperty(Count("attachments"))

    objects = QueryablePropertiesManager()
    # accounting_status = AnnotationProperty(
    #     Case(
    #         When(is_commerce=False, then=Value("-")),
    #         When(
    #             is_commerce=True,
    #             is_purchased_amortized=False,
    #             is_purchased_asset=False,
    #             then=Value("Unknown"),
    #         ),
    #         When(is_sold=True, then=Value("sold")),
    #         # When(is_amortized=True, then=Value("Amortized")),
    #         # When(is_commerce=True, is_sold=True, is_purchased_amortized=True, is_purchased_asset=False, then=Value("Sold")),
    #         # When(is_commerce=True, is_sold=True, is_purchased_amortized=False, is_purchased_asset=True, then=Value("Sold")),
    #         # When(is_commerce=True, is_sold=True, is_purchased_amortized=True, is_purchased_asset=False, is_amortized=False, then=Value("Sold (error)")),
    #         # When(is_commerce=True, is_sold=True, is_purchased_amortized=False, is_purchased_asset=True, is_amortized=False, then=Value("Sold (error)")),
    #         # When(is_sold=True, is_amortized=False, then=Value("Sold (error)")),
    #         When(is_rented=True, has_rental_agreement=True, then=Value("Rented")),
    #         When(
    #             is_rented=False,
    #             has_rental_agreement=True,
    #             then=Value("Rented (error)"),
    #         ),
    #         When(
    #             is_rented=True,
    #             has_rental_agreement=False,
    #             then=Value("Rented (error)"),
    #         ),
    #         When(is_rented=False, has_loan_agreement=True, then=Value("Loaned")),
    #         # When(
    #         #     is_sold=False,
    #         #     is_amortized=True,
    #         #     is_purchased_amortized=False,
    #         #     then=Value("Amortized"),
    #         # ),
    #         # When(
    #         #     is_amortized=True,
    #         #     is_purchased_amortized=True,
    #         #     then=Value("Available or amortized"),
    #         # ),
    #         default=Value("Available"),
    #     )
    # )

    is_on_journal_document_lines = RelatedExistenceCheckProperty(
        "journal_document_lines"
    )

    @property
    def accounting_status(self):
        if self.is_sold:
            return AccountingStates.SOLD
        if self.is_rented or self.has_rental_agreement:
            return AccountingStates.ISSUED_RENT
        if self.has_loan_agreement:
            return AccountingStates.ISSUED_LOAN
        if self.is_purchased_amortized:
            return AccountingStates.AVAILABLE_OR_AMORTIZED
        if self.is_amortized and self.is_on_journal_document_lines:
            return AccountingStates.AMORTIZED
        if self.is_on_journal_document_lines:
            return AccountingStates.AVAILABLE
        return AccountingStates.UNKNOWN

    @property
    def accounting_errors(self):
        errors = []

        if self.is_sold and self.is_rented:
            errors.append(_("Sold and rented"))
        if self.is_sold and not self.is_amortized:
            errors.append(_("Sold and not amortized"))
        if self.is_rented and not self.has_rental_agreement:
            errors.append(_("Rented and not rental agreement"))
        if self.is_rented and self.has_loan_agreement:
            errors.append(_("Rented and loan agreement"))
        if self.has_rental_agreement and not self.is_rented:
            errors.append(_("Rental agreement and not rented"))
        if self.has_rental_agreement and self.has_loan_agreement:
            errors.append(_("Rental agreement and loan agreement"))
        if self.num_loan_agreements > 1:
            errors.append(_("Multiple loan agreements"))
        if self.num_rental_agreements > 1:
            errors.append(_("Multiple rental agreements"))

        if self.purchase_value > Decimal(450) and self.is_purchased_amortized:
            errors.append(_("Amortized above 450 euro"))

        if not self.is_commerce:
            if self.is_sold:
                errors.append(_("Sold and not commerce"))
            if self.is_rented:
                errors.append(_("Rented and not commerce"))
            if self.has_rental_agreement:
                errors.append(_("Rental agreement and not commerce"))

        if self.is_margin and self.is_non_margin:
            errors.append(_("Margin asset on non-margin ledgers"))

        if not self.accounting_status_compatible_with_local_status:
            errors.append(_("Accounting status incompatible with local status"))

        if errors:
            return errors
        return None

    @property
    def accounting_status_compatible_with_local_status(self):
        if not self.is_commerce and self.accounting_status != AccountingStates.UNKNOWN:
            return False

        if self.accounting_status == AccountingStates.UNKNOWN:
            return True
        elif self.accounting_status == AccountingStates.AVAILABLE:
            if self.local_status in [
                AssetStates.AVAILABLE,
                AssetStates.MAINTENANCE_EXTERNAL,
                AssetStates.MAINTENANCE_IN_HOUSE,
                AssetStates.UNDER_REVIEW,
                AssetStates.ISSUED_UNPROCESSED,
                AssetStates.TO_BE_DELIVERED,
                AssetStates.PLACEHOLDER,
            ]:
                return True
            return False
        elif self.accounting_status == AccountingStates.AVAILABLE_OR_AMORTIZED:
            if self.local_status in [
                AssetStates.AVAILABLE,
                AssetStates.MAINTENANCE_EXTERNAL,
                AssetStates.MAINTENANCE_IN_HOUSE,
                AssetStates.UNDER_REVIEW,
                AssetStates.ISSUED_UNPROCESSED,
                AssetStates.TO_BE_DELIVERED,
                AssetStates.AMORTIZED,
            ]:
                return True
            return False
        elif self.accounting_status == AccountingStates.ISSUED_RENT:
            if self.local_status == AssetStates.ISSUED_RENT:
                return True
            return False
        elif self.accounting_status == AccountingStates.ISSUED_LOAN:
            if self.local_status == AssetStates.ISSUED_LOAN:
                return True
            return False
        elif self.accounting_status == AccountingStates.AMORTIZED:
            if self.local_status == AssetStates.AMORTIZED:
                return True
            return False
        elif self.accounting_status == AccountingStates.SOLD:
            if self.local_status == AssetStates.SOLD:
                return True
            return False

    @property
    def last_accounting_description(self):
        latest_asset_agreement = self.estimate_document_lines.latest(
            "document__created_at"
        )
        return latest_asset_agreement.description

    @property
    def last_accounting_price(self):
        latest_asset_agreement = self.estimate_document_lines.latest(
            "document__created_at"
        )
        return latest_asset_agreement.price

    def __str__(self):
        return f"{self.category.name_singular} {self.id} ({self.size})"

    def get_absolute_url(self):
        return reverse("admin:inventory_asset_view", args=[self.id])

    class Meta:
        ordering = ["-created_at", "id"]
        verbose_name = _("asset")
        verbose_name_plural = _("assets")

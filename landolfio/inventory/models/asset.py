from decimal import Decimal

from django.db import models
from django.db.models import (
    PROTECT,
    Sum,
    Q,
    F,
)
from django.db.models.functions import Coalesce
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
from inventory.models.status import AssetStates


class FilteredRelatedExistenceCheckProperty(RelatedExistenceCheckProperty):
    def __init__(self, check_property, filter=None, *args, **kwargs):
        super().__init__(check_property, *args, **kwargs)
        self.filter = filter

    def get_queryset(self, model):
        return super().get_queryset(model).filter(self.filter)


class Asset(models.Model):
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_("created at"))
    id = models.CharField(verbose_name=_("ID"), max_length=200, primary_key=True)
    category = models.ForeignKey(
        AssetCategory, null=True, blank=False, on_delete=PROTECT, verbose_name=_("category")
    )
    size = models.ForeignKey(AssetSize, null=True, blank=True, on_delete=PROTECT, verbose_name=_("size"))
    location = models.ForeignKey(
        AssetLocation, null=True, blank=True, on_delete=PROTECT, verbose_name=_("location")
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
        EstimateDocumentLine, through=AssetOnEstimateDocumentLine,
        verbose_name=_("estimate document lines"),
    )
    recurring_sales_invoice_document_lines = models.ManyToManyField(
        RecurringSalesInvoiceDocumentLine,
        through=AssetOnRecurringSalesInvoiceDocumentLine,
        verbose_name=_("recurring sales invoice document lines"),
    )

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
            journal_document_line_assets__document_line__ledger_account__is_margin=True
        ),
    )
    is_non_margin = FilteredRelatedExistenceCheckProperty(
        "journal_document_lines",
        filter=Q(
            journal_document_line_assets__document_line__ledger_account__is_margin=False
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

    objects = QueryablePropertiesManager()
    # moneybird_status = AnnotationProperty(
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

    @property
    def moneybird_status(self):
        error = self.check_moneybird_errors() is not None

        if not self.is_commerce:
            return None if not error else _("Error")
        if self.is_sold:
            return _("Sold") if not error else _("Sold (error)")
        if self.is_rented or self.has_rental_agreement:
            return _("Rented") if not error else _("Rented (error)")
        if self.has_loan_agreement:
            return _("Loaned") if not error else _("Loaned (error)")
        if self.is_amortized:
            if self.is_purchased_asset:
                return _("Amortized") if not error else _("Amortized (error)")
            return (
                _("Available or amortized")
                if not error
                else _("Available or amortized (error)")
            )

        return _("Available") if not error else _("Available (error)")

    def check_moneybird_errors(self):
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

        if not self.is_commerce:
            if self.is_sold:
                errors.append(_("Sold and not commerce"))
            if self.is_rented:
                errors.append(_("Rented and not commerce"))
            if self.has_rental_agreement:
                errors.append(_("Rental agreement and not commerce"))

        if self.is_margin and self.is_non_margin:
            errors.append(_("Margin asset on non-margin ledgers"))

        if errors:
            return errors
        return None

    def __str__(self):
        return f"{self.category.name_singular} {self.id} ({self.size})"

    class Meta:
        ordering = ["created_at", "id"]
        verbose_name = _("asset")
        verbose_name_plural = _("assets")

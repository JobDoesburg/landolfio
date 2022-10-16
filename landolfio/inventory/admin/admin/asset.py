from admin_numeric_filter.admin import SliderNumericFilter, NumericFilterModelAdmin
from django.urls import reverse
from django.utils.html import format_html

from autocompletefilter.admin import AutocompleteFilterMixin
from autocompletefilter.filters import AutocompleteListFilter
from django.contrib import admin
from django.utils.safestring import mark_safe
from django.utils.translation import gettext_lazy as _
from django.db.models.aggregates import Max
from queryable_properties.admin import (
    QueryablePropertiesAdminMixin,
)
from django_admin_multi_select_filter.filters import MultiSelectFieldListFilter

from accounting.models.ledger_account import LedgerAccountType
from inventory.models.asset import (
    Asset,
    AssetOnJournalDocumentLine,
    AssetOnEstimateDocumentLine,
    AssetOnRecurringSalesInvoiceDocumentLine,
)
from inventory.models.attachment import Attachment
from inventory.models.remarks import Remark


def is_an_image_path(path: str) -> bool:
    """Return true if the path points to an image."""
    extension = path.split(".")[-1]
    return extension in ("jpg", "jpeg", "png")


class AttachmentInlineAdmin(admin.StackedInline):
    """Attachment inline admin."""

    def show_image(self, obj):
        # pylint: disable=no-self-use
        """Show a file as an image if it is one."""
        if is_an_image_path(obj.attachment.name):
            return mark_safe(f'<img src="{obj.attachment.url}" height="600px"/>')
        return _("Not an image")

    show_image.short_description = _("Image")

    model = Attachment
    readonly_fields = ["show_image", "upload_date"]
    extra = 0


class RemarkInline(admin.StackedInline):
    model = Remark
    fields = ["date", "remark"]
    readonly_fields = ["date"]
    extra = 1

    def has_change_permission(self, request, obj=None):
        return False


class DocumentLineInline(QueryablePropertiesAdminMixin, admin.TabularInline):
    extra = 0
    can_delete = False

    @admin.display(description=_("Workflow"))
    def workflow(self, obj):
        return obj.document_line.document.workflow

    @admin.display(description=_("View on Moneybird"))
    def view_on_moneybird(self, obj):
        url = obj.document_line.document.moneybird_url

        if url is None:
            return None
        return mark_safe(
            f'<a class="button small" href="{url}" target="_blank" style="white-space: nowrap;">{_("View on Moneybird")}</a>'
        )

    def has_add_permission(self, request, obj):
        return False


class JournalDocumentLineInline(DocumentLineInline):
    model = AssetOnJournalDocumentLine

    fields = [
        "date",
        "description",
        "document",
        "workflow",
        "contact",
        "ledger_account",
        "value",
        "view_on_moneybird",
    ]

    readonly_fields = (
        "date",
        "description",
        "document",
        "workflow",
        "contact",
        "ledger_account",
        "value",
        "view_on_moneybird",
    )


class SalesAndPurchaseJournalDocumentLineInline(JournalDocumentLineInline):
    def get_queryset(self, request):
        return (
            super()
            .get_queryset(request)
            .exclude(
                document_line__ledger_account__account_type=LedgerAccountType.REVENUE,
                document_line__ledger_account__is_sales=False,
            )
            .exclude(
                document_line__ledger_account__account_type=LedgerAccountType.EXPENSES,
                document_line__ledger_account__is_purchase=False,
            )
        )


class NonSalesRevenueDocumentLineInline(JournalDocumentLineInline):
    def get_queryset(self, request):
        return (
            super()
            .get_queryset(request)
            .filter(
                document_line__ledger_account__account_type=LedgerAccountType.REVENUE,
                document_line__ledger_account__is_sales=False,
            )
        )


class NonPurchaseExpenseDocumentLineInline(JournalDocumentLineInline):
    def get_queryset(self, request):
        return (
            super()
            .get_queryset(request)
            .filter(
                document_line__ledger_account__account_type=LedgerAccountType.EXPENSES,
                document_line__ledger_account__is_purchase=False,
            )
        )


class EstimateDocumentLineInline(DocumentLineInline):
    model = AssetOnEstimateDocumentLine

    fields = [
        "date",
        "description",
        "document",
        "document_state",
        "workflow",
        "contact",
        "ledger_account",
        "value",
        "view_on_moneybird",
    ]

    readonly_fields = (
        "date",
        "description",
        "document",
        "document_state",
        "workflow",
        "contact",
        "ledger_account",
        "value",
        "view_on_moneybird",
    )

    @admin.display(description=_("Document state"))
    def document_state(self, obj):
        return obj.document_line.document.state


class RecurringSalesDocumentLineInline(DocumentLineInline):
    model = AssetOnRecurringSalesInvoiceDocumentLine

    fields = [
        "date",
        "description",
        "document",
        "active",
        "workflow",
        "contact",
        "ledger_account",
        "value",
        "view_on_moneybird",
    ]

    readonly_fields = (
        "date",
        "description",
        "document",
        "active",
        "workflow",
        "contact",
        "ledger_account",
        "value",
        "view_on_moneybird",
    )

    @admin.display(description=_("Active"), boolean=True)
    def active(self, obj):
        return obj.document_line.document.active


class ListingPriceSliderFilter(SliderNumericFilter):
    MAX_DECIMALS = 0
    MIN_VALUE = 0
    MAX_VALUE = Asset.objects.aggregate(Max("listing_price"))["listing_price__max"]
    STEP = 100


@admin.register(Asset)
class AssetAdmin(
    AutocompleteFilterMixin, QueryablePropertiesAdminMixin, NumericFilterModelAdmin
):
    list_display = (
        "id",
        "category",
        "size",
        "location",
        "collection",
        "listing_price",
        "accounting_status",
        "local_status",
        "is_margin",
        "is_amortized",
        "accounting_errors",
        # "total_assets_value",
        # "total_direct_costs_value",
        # "total_expenses_value",
        # "total_revenue_value",
        # "purchase_value",
        # "sales_profit",
        # "total_profit",
    )

    list_filter = (
        ("collection", AutocompleteListFilter),
        ("local_status", MultiSelectFieldListFilter),
        ("category", AutocompleteListFilter),
        ("size", AutocompleteListFilter),
        ("location", AutocompleteListFilter),
        ("location__location_group", AutocompleteListFilter),
        ("listing_price", ListingPriceSliderFilter),
        # "accounting_status",
        "is_sold",
        "is_margin",
        "is_purchased_asset",
        "is_purchased_amortized",
        "is_amortized",
        "has_rental_agreement",
        "has_loan_agreement",
        "is_rented",
    )

    search_fields = [
        "id",
        "remarks__remark",
        "category__name",
        "size__name",
        "location__name",
        "location__location_group__name",
        "collection__name",
        "journal_document_lines__description",
        "journal_document_lines__contact__first_name",
        "estimate_document_lines__description",
        "estimate_document_lines__document__contact__first_name",
        "estimate_document_lines__document__contact__last_name",
        "estimate_document_lines__document__contact__company_name",
        "recurring_sales_invoice_document_lines__description",
        "recurring_sales_invoice_document_lines__document__contact__first_name",
        "recurring_sales_invoice_document_lines__document__contact__last_name",
        "recurring_sales_invoice_document_lines__document__contact__company_name",
    ]

    fieldsets = [
        (
            "Name",
            {
                "fields": [
                    "id",
                    "category",
                    "size",
                    "location",
                    "collection",
                    "local_status",
                    "accounting_status",
                    "accounting_errors",
                    "listing_price",
                ],
            },
        ),
        (
            "Financial",
            {
                "fields": [
                    "total_assets_value",
                    "total_margin_assets_value",
                    "total_non_margin_assets_value",
                    "total_direct_costs_value",
                    "total_margin_direct_costs_value",
                    "total_non_margin_direct_costs_value",
                    "total_expenses_value",
                    "total_purchase_expenses",
                    "total_other_expenses",
                    "total_revenue_value",
                    "total_sales_revenue",
                    "total_sales_revenue_margin",
                    "total_sales_revenue_non_margin",
                    "total_other_revenue",
                    "purchase_value",
                    "sales_profit",
                    "total_profit",
                    "is_margin",
                    "is_non_margin",
                    "is_sold",
                    "is_sold_as_margin",
                    "is_sold_as_non_margin",
                    "is_purchased_asset",
                    "is_purchased_asset_as_margin",
                    "is_purchased_asset_as_non_margin",
                    "is_purchased_amortized",
                    "is_amortized",
                    "is_commerce",
                    "has_rental_agreement",
                    "has_loan_agreement",
                    "is_rented",
                ],
                "classes": ("collapse",),
            },
        ),
    ]

    readonly_fields = (
        "total_assets_value",
        "total_margin_assets_value",
        "total_non_margin_assets_value",
        "total_direct_costs_value",
        "total_margin_direct_costs_value",
        "total_non_margin_direct_costs_value",
        "total_expenses_value",
        "total_purchase_expenses",
        "total_other_expenses",
        "total_revenue_value",
        "total_sales_revenue",
        "total_sales_revenue_margin",
        "total_sales_revenue_non_margin",
        "total_other_revenue",
        "purchase_value",
        "sales_profit",
        "total_profit",
        "is_margin",
        "is_non_margin",
        "is_sold",
        "is_sold_as_margin",
        "is_sold_as_non_margin",
        "is_purchased_asset",
        "is_purchased_asset_as_margin",
        "is_purchased_asset_as_non_margin",
        "is_purchased_amortized",
        "is_amortized",
        "is_commerce",
        "has_rental_agreement",
        "has_loan_agreement",
        "is_rented",
        "accounting_status",
        "accounting_errors",
    )
    inlines = [
        RemarkInline,
        AttachmentInlineAdmin,
        JournalDocumentLineInline,
        SalesAndPurchaseJournalDocumentLineInline,
        NonSalesRevenueDocumentLineInline,
        NonPurchaseExpenseDocumentLineInline,
        EstimateDocumentLineInline,
        RecurringSalesDocumentLineInline,
    ]

    @admin.display(
        boolean=True,
        ordering="is_margin",
        description=_("margin"),
    )
    def is_margin(self, obj):
        return obj.is_margin

    @admin.display(
        boolean=True,
        ordering="is_non_margin",
        description=_("not margin"),
    )
    def is_non_margin(self, obj):
        return obj.is_non_margin

    @admin.display(
        boolean=True,
        ordering="is_sold",
        description=_("sold"),
    )
    def is_sold(self, obj):
        return obj.is_sold

    @admin.display(
        boolean=True,
        ordering="is_sold_as_margin",
        description=_("sold margin"),
    )
    def is_sold_as_margin(self, obj):
        return obj.is_sold_as_margin

    @admin.display(
        boolean=True,
        ordering="is_sold_as_non_margin",
        description=_("sold non margin"),
    )
    def is_sold_as_non_margin(self, obj):
        return obj.is_sold_as_non_margin

    @admin.display(
        boolean=True,
        ordering="is_purchased_asset",
        description=_("purchased asset"),
    )
    def is_purchased_asset(self, obj):
        return obj.is_purchased_asset

    @admin.display(
        boolean=True,
        ordering="is_purchased_asset_as_margin",
        description=_("purchased asset margin"),
    )
    def is_purchased_asset_as_margin(self, obj):
        return obj.is_purchased_asset_as_margin

    @admin.display(
        boolean=True,
        ordering="is_purchased_asset_as_non_margin",
        description=_("purchased asset non margin"),
    )
    def is_purchased_asset_as_non_margin(self, obj):
        return obj.is_purchased_asset_as_non_margin

    @admin.display(
        boolean=True,
        ordering="is_purchased_amortized",
        description=_("purchased amortized"),
    )
    def is_purchased_amortized(self, obj):
        return obj.is_purchased_amortized

    @admin.display(
        boolean=True,
        ordering="is_commerce",
        description=_("commerce"),
    )
    def is_commerce(self, obj):
        return obj.is_commerce

    @admin.display(
        boolean=True,
        ordering="is_amortized",
        description=_("amortized"),
    )
    def is_amortized(self, obj):
        return obj.is_amortized

    @admin.display(
        boolean=True,
        ordering="is_rented",
        description=_("rented"),
    )
    def is_rented(self, obj):
        return obj.is_rented

    @admin.display(
        boolean=True,
        ordering="has_rental_agreement",
        description=_("has rental agreement"),
    )
    def has_rental_agreement(self, obj):
        return obj.has_rental_agreement

    @admin.display(
        boolean=True,
        ordering="has_loan_agreement",
        description=_("has loan agreement"),
    )
    def has_loan_agreement(self, obj):
        return obj.has_loan_agreement

    def get_readonly_fields(self, request, obj=None):
        readonly_fields = super().get_readonly_fields(request, obj)
        if obj:
            readonly_fields += ("id",)
        return readonly_fields

    @admin.display(
        ordering="pk",
        description=_("asset"),
    )
    def asset_view_link(self, obj):
        return format_html(
            '<a href="{link}">{title}</a>',
            link=reverse("assets_admin:view_asset", kwargs={"id": obj.id}),
            title=obj.id,
        )

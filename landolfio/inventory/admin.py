from admin_numeric_filter.admin import SliderNumericFilter, NumericFilterModelAdmin
from django.contrib.admin import register
from django.db import models
from django.forms import CheckboxSelectMultiple
from django.urls import reverse, path
from django.utils.html import format_html

from autocompletefilter.admin import AutocompleteFilterMixin
from autocompletefilter.filters import AutocompleteListFilter
from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from queryable_properties.admin import (
    QueryablePropertiesAdminMixin,
    QueryablePropertiesAdmin,
)
from django_admin_multi_select_filter.filters import MultiSelectFieldListFilter

from accounting.models import (
    EstimateDocumentLine,
    JournalDocumentLine,
    RecurringSalesInvoiceDocumentLine,
)
from inventory.admin_inlines import (
    RemarkInline,
    AttachmentInlineAdmin,
    JournalDocumentLineInline,
    SalesAndPurchaseJournalDocumentLineInline,
    NonSalesRevenueDocumentLineInline,
    NonPurchaseExpenseDocumentLineInline,
    EstimateDocumentLineInline,
    RecurringSalesDocumentLineInline,
    AssetOnRecurringSalesInvoiceDocumentLineInline,
    AssetOnEstimateDocumentLineInline,
    AssetOnJournalDocumentLineInline,
)
from inventory.admin_views import ViewAssetView, AssetOverviewView
from inventory.models.asset import (
    Asset,
)
from inventory.models.attachment import Attachment
from inventory.models.category import AssetCategory, AssetSize
from inventory.models.collection import Collection
from inventory.models.location import AssetLocation, AssetLocationGroup
from moneybird.admin import MoneybirdResourceModelAdmin


class ListingPriceSliderFilter(SliderNumericFilter):
    MAX_DECIMALS = 0
    MIN_VALUE = 0
    STEP = 100


@register(Asset)
class AssetAdmin(
    AutocompleteFilterMixin, QueryablePropertiesAdminMixin, NumericFilterModelAdmin
):
    list_display = (
        "asset_view_link",
        "category",
        "size",
        "location",
        "collection",
        "listing_price",
        # "accounting_status",
        "local_status",
        "is_margin",
        "is_amortized",
        "attachment_count",
        # "accounting_errors",
        # "total_assets_value",
        # "total_direct_costs_value",
        # "total_expenses_value",
        # "total_revenue_value",
        # "purchase_value",
        # "sales_profit",
        # "total_profit",
    )

    list_filter = (
        "collection",
        ("local_status", MultiSelectFieldListFilter),
        "category",
        "size",
        "location",
        "location__location_group",
        ("listing_price", SliderNumericFilter),
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
        "tickets__description",
        "tickets__contact__first_name",
        "tickets__contact__last_name",
        "tickets__contact__company_name",
        "category__name",
        "size__name",
        # "location__name",
        # "location__location_group__name",
        "collection__name",
        # "journal_document_lines__description",
        # "journal_document_lines__contact__first_name",
        # "estimate_document_lines__description",
        # "estimate_document_lines__document__contact__first_name",
        # "estimate_document_lines__document__contact__last_name",
        # "estimate_document_lines__document__contact__company_name",
        # "recurring_sales_invoice_document_lines__description",
        # "recurring_sales_invoice_document_lines__document__contact__first_name",
        # "recurring_sales_invoice_document_lines__document__contact__last_name",
        # "recurring_sales_invoice_document_lines__document__contact__company_name",
    ]

    fieldsets = [
        (
            _("Name"),
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
            _("Financial"),
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

    autocomplete_fields = [
        "category",
        "size",
        "location",
        "collection",
    ]

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
        ordering="attachment_count",
        description=_("attachments"),
    )
    def attachment_count(self, obj):
        return obj.attachment_count

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
            f'<a href="{reverse("admin:inventory_asset_view", kwargs={"id": obj.id})}">{obj.id}</a>',
        )

    def get_search_results(self, request, queryset, search_term):
        """Override get_search_results to always search all objects, ignoring any filters."""
        if search_term:
            queryset = self.model.objects.all()
        queryset, use_distinct = super().get_search_results(
            request, queryset, search_term
        )
        return queryset, use_distinct

    def get_urls(self):
        urls = super().get_urls()
        my_urls = [
            path(
                "<path:id>/view/",
                self.admin_site.admin_view(
                    ViewAssetView.as_view(
                        extra_context={
                            "site_title": self.admin_site.site_title,
                            "site_header": self.admin_site.site_header,
                            "site_url": self.admin_site.site_url,
                            "has_permission": True,
                            "is_popup": False,
                            "show_assets_sidebar": True,
                            "categories": AssetCategory.objects.all().order_by("order"),
                            "locations": AssetLocation.objects.all().order_by("order"),
                            "collections": Collection.objects.all().order_by("order"),
                            "recent_assets": Asset.objects.all().order_by(
                                "-created_at"
                            )[:10],
                        },
                    )
                ),
                name="inventory_asset_view",
            ),
            path(
                "overview/",
                self.admin_site.admin_view(
                    AssetOverviewView.as_view(
                        extra_context={
                            "site_title": self.admin_site.site_title,
                            "site_header": self.admin_site.site_header,
                            "site_url": self.admin_site.site_url,
                            "has_permission": True,
                            "is_popup": False,
                            "show_assets_sidebar": True,
                            "categories": AssetCategory.objects.all().order_by("order"),
                            "locations": AssetLocation.objects.all().order_by("order"),
                            "collections": Collection.objects.all().order_by("order"),
                            "recent_assets": Asset.objects.all().order_by(
                                "-created_at"
                            )[:10],
                        },
                    )
                ),
                name="inventory_asset_overview",
            ),
            path(
                "overview/changelist/",
                self.overview_changelist_view,
                name="inventory_asset_overview_changelist",
            ),
        ]
        return my_urls + urls

    def overview_changelist_view(self, request, extra_context=None):
        extra_context = extra_context or {}
        extra_context["show_assets_sidebar"] = True
        return self.changelist_view(request, extra_context=extra_context)

    def changelist_view(self, request, extra_context=None):
        extra_context = extra_context or {}
        extra_context["categories"] = AssetCategory.objects.all().order_by("order")
        extra_context["locations"] = AssetLocation.objects.all().order_by("order")
        extra_context["collections"] = Collection.objects.all().order_by("order")
        extra_context["recent_assets"] = Asset.objects.all().order_by("-created_at")[
            :10
        ]
        return super().changelist_view(request, extra_context=extra_context)

    def add_view(self, request, form_url="", extra_context=None):
        extra_context = extra_context or {"is_nav_sidebar_enabled": False}
        return super().add_view(request, form_url, extra_context=extra_context)


@admin.register(Collection)
class CollectionAdmin(admin.ModelAdmin):
    search_fields = ["name"]
    ordering = ["id"]


@admin.register(Attachment)
class AttachmentAdmin(admin.ModelAdmin):
    list_display = (
        "asset",
        "attachment",
        "upload_date",
    )
    date_hierarchy = "upload_date"
    readonly_fields = ["upload_date"]


@admin.register(AssetCategory)
class AssetCategoryAdmin(admin.ModelAdmin):
    search_fields = ["name"]


@admin.register(AssetSize)
class AssetSizeAdmin(admin.ModelAdmin):
    formfield_overrides = {
        models.ManyToManyField: {"widget": CheckboxSelectMultiple},
    }
    search_fields = ["name"]


@admin.register(AssetLocation)
class AssetLocationAdmin(admin.ModelAdmin):
    formfield_overrides = {
        models.ManyToManyField: {"widget": CheckboxSelectMultiple},
    }

    search_fields = ["name"]


@admin.register(AssetLocationGroup)
class AssetLocationGroupAdmin(admin.ModelAdmin):
    search_fields = ["name"]


@admin.register(JournalDocumentLine)
class JournalDocumentLineAdmin(
    AutocompleteFilterMixin, QueryablePropertiesAdmin, MoneybirdResourceModelAdmin
):
    list_display = (
        "description",
        "document",
        "date",
        "assets",
        "total_amount",
        "ledger_account",
    )
    list_display_links = ["description", "document", "date"]
    search_fields = ["description", "assets__id"]
    readonly_fields = ["assets"]
    inlines = [AssetOnJournalDocumentLineInline]
    list_filter = [
        ("assets", admin.EmptyFieldListFilter),
        ("assets__asset", AutocompleteListFilter),
        ("assets__asset__category", AutocompleteListFilter),
        ("ledger_account", AutocompleteListFilter),
        "ledger_account__account_type",
    ]

    def get_queryset(self, request):
        return super().get_queryset(request).select_subclasses()

    @admin.display(description=_("assets"))
    def assets(self, obj):
        return ", ".join(obj.assets.values_list("asset", flat=True))

    def has_add_permission(self, request, obj=None):
        return False


@admin.register(EstimateDocumentLine)
class EstimateDocumentLineAdmin(
    AutocompleteFilterMixin, QueryablePropertiesAdmin, MoneybirdResourceModelAdmin
):
    list_display = (
        "description",
        "document",
        "date",
        "assets",
        "total_amount",
        "ledger_account",
    )
    list_display_links = ["description", "document", "date"]
    search_fields = ["description", "assets__id"]
    readonly_fields = ["assets"]
    inlines = [AssetOnEstimateDocumentLineInline]
    list_filter = [
        ("assets", admin.EmptyFieldListFilter),
        ("assets__asset", AutocompleteListFilter),
        ("assets__asset__category", AutocompleteListFilter),
        ("document__workflow", AutocompleteListFilter),
    ]

    @admin.display(description=_("assets"))
    def assets(self, obj):
        return ", ".join(obj.assets.values_list("asset", flat=True))

    def has_add_permission(self, request, obj=None):
        return False


@admin.register(RecurringSalesInvoiceDocumentLine)
class RecurringSalesInvoiceDocumentLineAdmin(
    AutocompleteFilterMixin, QueryablePropertiesAdmin, MoneybirdResourceModelAdmin
):
    list_display = (
        "description",
        "document",
        "date",
        "assets",
        "total_amount",
        "ledger_account",
    )
    list_display_links = ["description", "document", "date"]
    search_fields = ["description", "assets__id"]
    readonly_fields = ["assets"]
    inlines = [AssetOnRecurringSalesInvoiceDocumentLineInline]
    list_filter = [
        ("assets", admin.EmptyFieldListFilter),
        ("assets__asset", AutocompleteListFilter),
        ("assets__asset__category", AutocompleteListFilter),
        ("document__workflow", AutocompleteListFilter),
        ("ledger_account", AutocompleteListFilter),
        "ledger_account__account_type",
    ]

    @admin.display(description=_("assets"))
    def assets(self, obj):
        return ", ".join(obj.assets.values_list("asset", flat=True))

    def has_add_permission(self, request, obj=None):
        return False

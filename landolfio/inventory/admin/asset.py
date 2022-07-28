# from admin_numeric_filter.admin import SliderNumericFilter, NumericFilterModelAdmin
from autocompletefilter.admin import AutocompleteFilterMixin
from autocompletefilter.filters import AutocompleteListFilter
from django.contrib import admin
from django.utils.safestring import mark_safe
from django.utils.translation import gettext as _
from queryable_properties.admin import QueryablePropertiesAdmin

from inventory.models.asset import (
    Asset,
    AssetOnJournalDocumentLine,
)
from inventory.models.attachment import Attachment


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


class JournalDocumentLineInline(admin.TabularInline):
    model = AssetOnJournalDocumentLine
    extra = 0
    can_delete = False
    show_change_link = True

    fields = [
        "_date",
        "_description",
        "_contact",
        "_ledger_account",
        "value",
        "view_on_moneybird",
    ]

    readonly_fields = (
        "_date",
        "_description",
        "_contact",
        "_ledger_account",
        "value",
        "view_on_moneybird",
    )

    @admin.display
    def _date(self, obj):
        return obj.document_line.document.date

    @admin.display
    def _description(self, obj):
        return obj.document_line.description

    @admin.display
    def _contact(self, obj):
        return obj.document_line.document.contact

    @admin.display
    def _ledger_account(self, obj):
        return obj.document_line.ledger_account

    @admin.display(description="View on Moneybird")
    def view_on_moneybird(self, obj):
        url = obj.document_line.document.moneybird_url
        if url is None:
            return None
        return mark_safe(
            f'<a class="button small" href="{url}" target="_blank" style="white-space: nowrap;">View on Moneybird</a>'
        )

    def has_add_permission(self, request, obj):
        return False


# class ListingPriceSliderFilter(SliderNumericFilter):
#     MAX_DECIMALS = 0
#     STEP = 50


@admin.register(Asset)
class AssetAdmin(AutocompleteFilterMixin, QueryablePropertiesAdmin):
    """Asset admin."""

    list_display = (
        "id",
        "category",
        "size",
        "location",
        "collection",
        "listing_price",
        "is_margin",
        "purchase_value",
        "is_purchased_asset",
        "is_amortized",
        "moneybird_status",
        "local_status",
        # "check_moneybird_errors",
        "total_assets_value",
        "total_direct_costs_value",
        "total_expenses_value",
        "total_revenue_value",
        "purchase_value",
        "sales_profit",
        "total_profit",
    )

    list_filter = (
        ("category", AutocompleteListFilter),
        ("size", AutocompleteListFilter),
        ("collection", AutocompleteListFilter),
        "local_status",
        "moneybird_status",
        ("location", AutocompleteListFilter),
        ("location__location_group", AutocompleteListFilter),
        "is_margin",
        "is_purchased_asset",
        "is_purchased_amortized",
        "is_amortized",
        # ("listing_price", ListingPriceSliderFilter),
    )

    search_fields = [
        "id",
        "remarks",
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
                    "moneybird_status",
                    "check_moneybird_errors",
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
                ],
                "classes": ("collapse",),
            },
        ),
        (
            "Detail",
            {
                "fields": [
                    "remarks",
                ],
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
        "moneybird_status",
        "check_moneybird_errors",
    )
    inlines = [AttachmentInlineAdmin, JournalDocumentLineInline]

    @admin.display(
        boolean=True,
        ordering="is_margin",
        description="margin",
    )
    def is_margin(self, obj):
        return obj.is_margin

    @admin.display(
        boolean=True,
        ordering="is_non_margin",
        description="not margin",
    )
    def is_non_margin(self, obj):
        return obj.is_non_margin

    @admin.display(
        boolean=True,
        ordering="is_sold",
        description="sold",
    )
    def is_sold(self, obj):
        return obj.is_sold

    @admin.display(
        boolean=True,
        ordering="is_sold_as_margin",
        description="sold margin",
    )
    def is_sold_as_margin(self, obj):
        return obj.is_sold_as_margin

    @admin.display(
        boolean=True,
        ordering="is_sold_as_non_margin",
        description="sold non margin",
    )
    def is_sold_as_non_margin(self, obj):
        return obj.is_sold_as_non_margin

    @admin.display(
        boolean=True,
        ordering="is_purchased_asset",
        description="purchased asset",
    )
    def is_purchased_asset(self, obj):
        return obj.is_purchased_asset

    @admin.display(
        boolean=True,
        ordering="is_purchased_asset_as_margin",
        description="purchased asset margin",
    )
    def is_purchased_asset_as_margin(self, obj):
        return obj.is_purchased_asset_as_margin

    @admin.display(
        boolean=True,
        ordering="is_purchased_asset_as_non_margin",
        description="purchased asset non margin",
    )
    def is_purchased_asset_as_non_margin(self, obj):
        return obj.is_purchased_asset_as_non_margin

    @admin.display(
        boolean=True,
        ordering="is_purchased_amortized",
        description="purchased amortized",
    )
    def is_purchased_amortized(self, obj):
        return obj.is_purchased_amortized

    @admin.display(
        boolean=True,
        ordering="is_commerce",
        description="commerce",
    )
    def is_commerce(self, obj):
        return obj.is_commerce

    @admin.display(
        boolean=True,
        ordering="is_amortized",
        description="amortized",
    )
    def is_amortized(self, obj):
        return obj.is_amortized

    def get_readonly_fields(self, request, obj=None):
        readonly_fields = super().get_readonly_fields(request, obj)
        if obj:
            readonly_fields += ("id",)
        return readonly_fields

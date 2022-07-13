"""Inventory admin configuration."""
# from admin_numeric_filter.admin import SliderNumericFilter, NumericFilterModelAdmin
from admin_numeric_filter.admin import SliderNumericFilter, NumericFilterModelAdmin
from django.contrib import admin
from django.core.exceptions import ObjectDoesNotExist
from django.db import models
from django.forms import CheckboxSelectMultiple
from django.utils.safestring import mark_safe
from django.utils.translation import gettext as _
from queryable_properties.admin import QueryablePropertiesAdmin

from .models import Asset, AssetLocation, AssetLocationGroup, AssetSize, AssetCategory
from .models import Attachment
from .models import Collection
from accounting.models import JournalDocument, JournalDocumentLine


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
    model = JournalDocumentLine
    extra = 0
    can_delete = False

    fields = [
        "_date",
        "document",
        "price",
        "ledger",
        "_moneybird_button",
    ]

    readonly_fields = (
        "_date",
        "_moneybird_button",
    )

    def _date(self, obj):
        return obj.document.date

    def _moneybird_button(self, obj):
        return mark_safe(
            f"<a class='button small' href='{obj.document.moneybird_url}' target='blank'>Go to Moneybird</a>"
        )

    def has_add_permission(self, request, obj):
        return False

    def has_change_permission(self, request, obj=None):
        return False


class ListingPriceSliderFilter(SliderNumericFilter):
    MAX_DECIMALS = 0
    STEP = 50


@admin.register(Asset)
class AssetAdmin(QueryablePropertiesAdmin, NumericFilterModelAdmin):
    """Asset admin."""

    model = Asset

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
        "check_moneybird_errors",
    )

    list_filter = (
        "category",
        "size",
        "location",
        "location__location_group",
        "collection",
        "moneybird_status",
        "is_margin",
        "is_purchased_asset",
        "is_purchased_amortized",
        "is_amortized",
        ("listing_price", ListingPriceSliderFilter),
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
                ],
            },
        ),
        (
            "Financial",
            {
                "fields": [
                    "listing_price",
                    "purchase_value",
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
                    "is_margin",
                    "is_non_margin",
                    "is_sold",
                    "is_sold_as_margin",
                    "is_sold_as_non_margin",
                    "is_purchased_asset",
                    "is_purchased_asset_as_margin",
                    "is_purchased_asset_as_non_margin",
                    "is_purchased_amortized",
                    "sales_profit",
                    "total_profit",
                    "is_amortized",
                    "is_commerce",
                    "moneybird_status",
                    "check_moneybird_errors",
                    "local_state",
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
        "purchase_value",
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
        "is_margin",
        "is_non_margin",
        "is_sold",
        "is_sold_as_margin",
        "is_sold_as_non_margin",
        "is_purchased_asset",
        "is_purchased_asset_as_margin",
        "is_purchased_asset_as_non_margin",
        "is_purchased_amortized",
        "sales_profit",
        "total_profit",
        "is_amortized",
        "is_commerce",
        "moneybird_status",
        "check_moneybird_errors",
    )
    inlines = [AttachmentInlineAdmin, JournalDocumentLineInline]

    @admin.display(boolean=True)
    def is_margin(self, obj):
        return obj.is_margin

    @admin.display(boolean=True)
    def is_non_margin(self, obj):
        return obj.is_non_margin

    @admin.display(boolean=True)
    def is_sold(self, obj):
        return obj.is_sold

    @admin.display(boolean=True)
    def is_sold_as_margin(self, obj):
        return obj.is_sold_as_margin

    @admin.display(boolean=True)
    def is_sold_as_non_margin(self, obj):
        return obj.is_sold_as_non_margin

    @admin.display(boolean=True)
    def is_purchased_asset(self, obj):
        return obj.is_purchased_asset

    @admin.display(boolean=True)
    def is_purchased_asset_as_margin(self, obj):
        return obj.is_purchased_asset_as_margin

    @admin.display(boolean=True)
    def is_purchased_asset_as_non_margin(self, obj):
        return obj.is_purchased_asset_as_non_margin

    @admin.display(boolean=True)
    def is_purchased_amortized(self, obj):
        return obj.is_purchased_amortized

    @admin.display(boolean=True)
    def is_commerce(self, obj):
        return obj.is_commerce

    @admin.display(boolean=True)
    def is_amortized(self, obj):
        return obj.is_amortized

    def changeform_view(self, request, object_id=None, form_url="", extra_context=None):
        """Render the change page for an Asset."""
        if extra_context is None:
            extra_context = {}

        try:
            asset = Asset.objects.get(pk=object_id)
            related_document_ids = asset.journal_document_lines.values_list(
                "document", flat=True
            )
            related_documents = JournalDocument.objects.filter(
                pk__in=set(related_document_ids)
            )
        except ObjectDoesNotExist:
            related_documents = None

        extra_context["related_documents"] = related_documents

        return super().changeform_view(request, object_id, form_url, extra_context)


@admin.register(Collection)
class CollectionAdmin(admin.ModelAdmin):
    """Collection admin."""

    model = Collection
    list_display = ("id", "name")


@admin.register(Attachment)
class AttachmentAdmin(admin.ModelAdmin):
    """Attachments admin."""

    model = Attachment
    list_display = ("asset", "attachment", "upload_date", "remarks")
    readonly_fields = ["upload_date"]


@admin.register(AssetCategory)
class AssetTypeAdmin(admin.ModelAdmin):
    class Media:
        """Necessary to use AutocompleteFilter."""


@admin.register(AssetSize)
class AssetSizeAdmin(admin.ModelAdmin):
    class Media:
        """Necessary to use AutocompleteFilter."""


@admin.register(AssetLocation)
class AssetLocationAdmin(admin.ModelAdmin):
    class Media:
        """Necessary to use AutocompleteFilter."""

    formfield_overrides = {
        models.ManyToManyField: {"widget": CheckboxSelectMultiple},
    }


@admin.register(AssetLocationGroup)
class AssetLocationGroupAdmin(admin.ModelAdmin):
    class Media:
        """Necessary to use AutocompleteFilter."""

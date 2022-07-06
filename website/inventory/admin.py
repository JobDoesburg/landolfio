"""Inventory admin configuration."""
# from admin_numeric_filter.admin import SliderNumericFilter, NumericFilterModelAdmin
from django.contrib import admin
from django.core.exceptions import ObjectDoesNotExist
from django.db import models
from django.forms import CheckboxSelectMultiple
from django.utils.safestring import mark_safe
from django.utils.translation import gettext as _

from .models import Asset, AssetLocation, AssetLocationGroup, AssetSize, AssetCategory
from .models import Attachment
from .models import Collection
from accounting.models import JournalDocument, JournalDocumentLine, LedgerKind


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


class SalesDocumentInline(JournalDocumentLineInline):
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        qs = qs.filter(
            ledger__kind__in=[
                LedgerKind.VERKOOP_MARGE.value,
                LedgerKind.VERKOOP_NIET_MARGE.value,
            ]
        )
        return qs


class PurchaseDocumentInline(JournalDocumentLineInline):
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        qs = qs.filter(
            ledger__kind__in=[
                LedgerKind.VOORRAAD_MARGE.value,
                LedgerKind.VOORRAAD_NIET_MARGE.value,
                LedgerKind.DIRECTE_AFSCHRIJVING.value,
            ]
        )
        return qs


# class ListingPriceSliderFilter(SliderNumericFilter):
#     MAX_DECIMALS = 0
#     STEP = 50


@admin.register(Asset)
class AssetAdmin(admin.ModelAdmin):  # and NumericFilterModelAdmin
    """Asset admin."""

    model = Asset

    list_display = (
        "id",
        "category",
        "size",
        "location",
        "collection",
        "listing_price",
        "stock_value",
        "amortization_value",
        "sales_value",
        "purchase_value",
        "is_margin",
        "is_sold",
        "is_amortized_not_at_purchase",
        "is_amortized_at_purchase",
        "is_amortized",
        "ledger_amounts",
        "moneybird_status",
        "check_moneybird_errors",
    )
    list_filter = (
        "category",
        "size",
        "location",
        "location__location_group",
        "collection",
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
                ]
            },
        ),
        (
            "Financial",
            {
                "fields": [
                    "listing_price",
                    "stock_value",
                    "amortization_value",
                    "sales_value",
                    "purchase_value",
                    "is_margin",
                    "is_sold",
                    "is_amortized_not_at_purchase",
                    "is_amortized_at_purchase",
                    "is_amortized",
                    "ledger_amounts",
                    "moneybird_status",
                    "check_moneybird_errors",
                    "local_state",
                ]
            },
        ),
        (
            "Detail",
            {
                "fields": [
                    "remarks",
                ]
            },
        ),
    ]

    readonly_fields = (
        "stock_value",
        "amortization_value",
        "sales_value",
        "purchase_value",
        "ledger_amounts",
        "is_margin",
        "is_sold",
        "is_amortized_not_at_purchase",
        "is_amortized_at_purchase",
        "is_amortized",
        "moneybird_status",
        "check_moneybird_errors",
    )
    inlines = [AttachmentInlineAdmin, JournalDocumentLineInline]

    def is_margin(self, obj):
        return obj.is_margin

    is_margin.boolean = True

    def is_sold(self, obj):
        return obj.is_sold

    is_sold.boolean = True

    def is_amortized_not_at_purchase(self, obj):
        return obj.is_amortized_not_at_purchase

    is_amortized_not_at_purchase.boolean = True

    def is_amortized_at_purchase(self, obj):
        return obj.is_amortized_at_purchase

    is_amortized_at_purchase.boolean = True

    def is_amortized(self, obj):
        return obj.is_amortized

    is_amortized.boolean = True

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

from admin_numeric_filter.admin import SliderNumericFilter, NumericFilterModelAdmin
from admin_numeric_filter.forms import SliderNumericForm
from django.contrib.admin import register
from django.db import models
from django.db.models import Max, Min
from django.forms import CheckboxSelectMultiple
from django.urls import reverse, path
from django.utils.html import format_html
from django.db.models.fields import DecimalField, FloatField

from autocompletefilter.admin import AutocompleteFilterMixin
from autocompletefilter.filters import AutocompleteListFilter
from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from queryable_properties.admin import (
    QueryablePropertiesAdminMixin,
    QueryablePropertiesAdmin,
)
from django_admin_multi_select_filter.filters import (
    MultiSelectFieldListFilter,
    MultiSelectRelatedFieldListFilter,
)

from inventory.admin_inlines import (
    RemarkInline,
    AttachmentInlineAdmin,
)
from inventory.admin_views import ViewAssetView, AssetOverviewView
from inventory.models.asset import (
    Asset,
)
from inventory.models.asset_property import AssetProperty, AssetPropertyValue
from inventory.models.attachment import Attachment
from inventory.models.category import Category, Size
from inventory.models.collection import Collection
from inventory.models.location import Location, LocationGroup


class AssetPropertyValueInline(admin.TabularInline):
    """Inline for editing asset property values directly on the asset."""

    model = AssetPropertyValue
    extra = 0
    fields = ["property", "value"]

    def get_queryset(self, request):
        return super().get_queryset(request).select_related("property")

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "property" and hasattr(self, "parent_obj"):
            # Filter properties that apply to the asset's category
            kwargs["queryset"] = AssetProperty.objects.filter(
                categories=self.parent_obj.category
            )
        return super().formfield_for_foreignkey(db_field, request, **kwargs)


class ListingPriceSliderFilter(SliderNumericFilter):
    MAX_DECIMALS = 0
    MIN_VALUE = 0
    STEP = 100

    def choices(self, changelist):
        total = changelist.queryset.all().count()
        min_value = changelist.queryset.aggregate(min=Min(self.parameter_name)).get(
            "min", 0
        )

        if total > 1:
            max_value = changelist.queryset.aggregate(max=Max(self.parameter_name)).get(
                "max", 0
            )
        else:
            max_value = None

        if isinstance(self.field, (FloatField, DecimalField)):
            decimals = self.MAX_DECIMALS
            step = self.STEP if self.STEP else self._get_min_step(self.MAX_DECIMALS)
        else:
            decimals = 0
            step = self.STEP if self.STEP else 1

        return (
            {
                "decimals": decimals,
                "step": step,
                "parameter_name": self.parameter_name,
                "request": self.request,
                "min": min_value,
                "max": max_value,
                "value_from": self.used_parameters.get(
                    self.parameter_name + "_from", min_value
                ),
                "value_to": self.used_parameters.get(
                    self.parameter_name + "_to", max_value
                ),
                "form": SliderNumericForm(
                    name=self.parameter_name,
                    data={
                        self.parameter_name
                        + "_from": self.used_parameters.get(
                            self.parameter_name + "_from", min_value
                        ),
                        self.parameter_name
                        + "_to": self.used_parameters.get(
                            self.parameter_name + "_to", max_value
                        ),
                    },
                ),
            },
        )


@register(Asset)
class AssetAdmin(
    AutocompleteFilterMixin, QueryablePropertiesAdminMixin, NumericFilterModelAdmin
):
    show_facets = admin.ShowFacets.NEVER

    list_display = (
        "asset_view_link",
        "category",
        "size",
        "location",
        "asset_location_nr",
        "collection",
        "listing_price",
        # "accounting_status",
        "local_status",
        "is_margin_asset_display",
        "is_disposed_display",
        "disposal_reason",
        "attachment_count",
        "start_date",
        "moneybird_asset_link",
    )

    list_filter = (
        ("collection", MultiSelectRelatedFieldListFilter),
        ("local_status", MultiSelectFieldListFilter),
        "category",
        "size",
        ("location", MultiSelectRelatedFieldListFilter),
        ("location__location_group", MultiSelectRelatedFieldListFilter),
        ("listing_price", ListingPriceSliderFilter),
        "is_margin_asset",
        "disposal",
    )

    search_fields = [
        "name",
        "remarks__remark",
        "tickets__description",
        "tickets__contact__first_name",
        "tickets__contact__last_name",
        "tickets__contact__company_name",
        "category__name",
        "size__name",
        "collection__name",
    ]

    fieldsets = [
        (
            _("Name"),
            {
                "fields": [
                    "id",
                    "name",
                    "category",
                    "size",
                    "location",
                    "location_nr",
                    "collection",
                    "local_status",
                    "listing_price",
                    "created_at",
                    "start_date",
                    "moneybird_asset_id",
                    "moneybird_asset_url",
                    "is_margin_asset",
                    "purchase_value_asset",
                ],
            },
        ),
        (
            _("Financial"),
            {
                "fields": [
                    "disposal",
                ],
                "classes": ("collapse",),
            },
        ),
    ]

    readonly_fields = (
        "id",
        "created_at",
        "moneybird_asset_url",
        "disposal",
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
        AssetPropertyValueInline,
    ]

    @admin.display(
        ordering="location_nr",
        description=_("nr"),
    )
    def asset_location_nr(self, obj):
        if obj.location:
            return obj.location_nr

    @admin.display(
        ordering="attachment_count",
        description=_("attachments"),
    )
    def attachment_count(self, obj):
        return obj.attachment_count

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

    @admin.display(
        ordering="name",
        description=_("asset"),
    )
    def asset_view_link(self, obj):
        return format_html(
            f'<a href="{reverse("admin:inventory_asset_view", kwargs={"id": obj.id})}">{obj.name}</a>',
        )

    @admin.display(
        boolean=True,
        ordering="is_margin_asset",
        description=_("margin asset"),
    )
    def is_margin_asset_display(self, obj):
        return obj.is_margin_asset

    @admin.display(
        ordering="start_date",
        description=_("start date"),
    )
    def start_date(self, obj):
        return obj.start_date

    @admin.display(
        description=_("Moneybird Asset"),
    )
    def moneybird_asset_link(self, obj):
        if obj.moneybird_asset_id:
            from django.conf import settings

            administration_id = getattr(settings, "MONEYBIRD_ADMINISTRATION_ID", None)
            if administration_id:
                url = f"https://moneybird.com/{administration_id}/assets/{obj.moneybird_asset_id}"
                return format_html(
                    '<a href="{}" target="_blank">{}</a>', url, obj.moneybird_asset_id
                )
            return obj.moneybird_asset_id
        return "-"

    @admin.display(
        description=_("Moneybird Asset URL"),
    )
    def moneybird_asset_url(self, obj):
        if obj.moneybird_asset_id:
            from django.conf import settings

            administration_id = getattr(settings, "MONEYBIRD_ADMINISTRATION_ID", None)
            if administration_id:
                url = f"https://moneybird.com/{administration_id}/assets/{obj.moneybird_asset_id}"
                return format_html('<a href="{}" target="_blank">{}</a>', url, url)
            return f"Moneybird asset ID: {obj.moneybird_asset_id} (MONEYBIRD_ADMINISTRATION_ID not set)"
        return "Not linked to Moneybird"

    @admin.display(
        boolean=True,
        ordering="disposal",
        description=_("disposed"),
    )
    def is_disposed_display(self, obj):
        return obj.is_disposed

    @admin.display(
        ordering="disposal",
        description=_("disposal reason"),
    )
    def disposal_reason(self, obj):
        return obj.disposal_reason_display if obj.is_disposed else "-"

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
                "<uuid:id>/view/",
                self.admin_site.admin_view(
                    ViewAssetView.as_view(
                        extra_context={
                            "site_title": self.admin_site.site_title,
                            "site_header": self.admin_site.site_header,
                            "site_url": self.admin_site.site_url,
                            "has_permission": True,
                            "is_popup": False,
                            "show_assets_sidebar": True,
                            "categories": Category.objects.all().order_by("order"),
                            "locations": Location.objects.all().order_by("order"),
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
                            "categories": Category.objects.all().order_by("order"),
                            "locations": Location.objects.all().order_by("order"),
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
        extra_context["categories"] = Category.objects.all().order_by("order")
        extra_context["locations"] = Location.objects.all().order_by("order")
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


@admin.register(Category)
class AssetCategoryAdmin(admin.ModelAdmin):
    search_fields = ["name"]


@admin.register(Size)
class AssetSizeAdmin(admin.ModelAdmin):
    formfield_overrides = {
        models.ManyToManyField: {"widget": CheckboxSelectMultiple},
    }
    search_fields = ["name"]


@admin.register(Location)
class AssetLocationAdmin(admin.ModelAdmin):
    formfield_overrides = {
        models.ManyToManyField: {"widget": CheckboxSelectMultiple},
    }

    search_fields = ["name"]


@admin.register(LocationGroup)
class AssetLocationGroupAdmin(admin.ModelAdmin):
    search_fields = ["name"]


@admin.register(AssetProperty)
class AssetPropertyAdmin(admin.ModelAdmin):
    """Admin interface for managing asset properties."""

    list_display = ["name", "get_categories", "property_type", "unit", "order"]
    list_filter = [
        "categories",
        "property_type",
    ]
    search_fields = ["name", "categories__name"]
    ordering = ["name", "order"]

    def get_categories(self, obj):
        return ", ".join([cat.name for cat in obj.categories.all()])

    get_categories.short_description = _("Categories")

    fieldsets = (
        (
            _("Basic Information"),
            {"fields": ("categories", "name", "property_type", "order")},
        ),
        (
            _("Type-Specific Settings"),
            {
                "fields": ("unit", "dropdown_options"),
                "description": _(
                    'Unit is used for numeric properties. Dropdown options should be a JSON array like ["Option 1", "Option 2"]'
                ),
            },
        ),
    )

    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        # Add help text for dropdown options
        if "dropdown_options" in form.base_fields:
            form.base_fields["dropdown_options"].widget.attrs.update(
                {
                    "placeholder": '["Red", "Blue", "Green"]',
                    "rows": 3,
                }
            )
        return form


@admin.register(AssetPropertyValue)
class AssetPropertyValueAdmin(admin.ModelAdmin):
    """Admin interface for managing individual asset property values."""

    list_display = ["asset", "property", "value", "get_formatted_value"]
    list_filter = [
        ("asset__category", AutocompleteListFilter),
        ("property", AutocompleteListFilter),
        "property__property_type",
    ]
    search_fields = ["asset__name", "property__name", "value"]
    autocomplete_fields = ["asset", "property"]

    def get_queryset(self, request):
        return (
            super()
            .get_queryset(request)
            .select_related("asset", "property", "asset__category")
        )

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "property" and hasattr(request, "_asset_category"):
            # Filter properties that apply to the category if we know the asset's category
            kwargs["queryset"] = AssetProperty.objects.filter(
                categories=request._asset_category
            )
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

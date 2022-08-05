from django.urls import path
from django.contrib import admin

from autocompletefilter.filters import AutocompleteListFilter

from inventory.models.asset import (
    Asset,
)
from inventory.admin.admin.asset import AssetAdmin as BaseAssetAdmin
from inventory.admin.assets_admin.views import ViewAssetView
from website.multi_select_filter import MultiSelectFieldListFilter
from inventory.admin.assets_admin.site import assets_admin
from inventory.admin.assets_admin.utils import get_extra_assets_context


class AssetAdmin(BaseAssetAdmin):
    change_list_template = "assets_admin/change_list.html"
    change_form_template = "assets_admin/change_form.html"

    list_display = (
        "asset_view_link",
        "category",
        "size",
        "location",
        "collection",
        "listing_price",
        # "moneybird_status",
        "local_status",
        "is_margin",
        "is_amortized",
    )

    list_filter = (
        ("attachments", admin.EmptyFieldListFilter),
        # "moneybird_status",
        ("local_status", MultiSelectFieldListFilter),
        ("category", AutocompleteListFilter),
        ("size", AutocompleteListFilter),
        ("collection", AutocompleteListFilter),
        ("location", AutocompleteListFilter),
        ("location__location_group", AutocompleteListFilter),
        "is_margin",
        "is_amortized",
        "has_rental_agreement",
        "has_loan_agreement",
        "is_rented",
        # ("listing_price", ListingPriceSliderFilter),
    )

    inlines = []

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
        "moneybird_status",
        "check_moneybird_errors",
    )

    def changelist_view(self, request, extra_context=None):
        extra_context = extra_context or {}
        extra_context = get_extra_assets_context(extra_context)
        return super().changelist_view(request, extra_context=extra_context)

    def add_view(self, request, form_url="", extra_context=None):
        extra_context = extra_context or {}
        extra_context = get_extra_assets_context(extra_context)
        return super().add_view(request, form_url, extra_context=extra_context)

    def changeform_view(self, request, object_id=None, form_url="", extra_context=None):
        extra_context = extra_context or {}
        extra_context = get_extra_assets_context(extra_context)
        return super().changeform_view(request, object_id, form_url, extra_context=extra_context)

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
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
                        },
                    )
                ),
                name="view_asset",
            ),
        ]
        return custom_urls + urls


assets_admin.register(Asset, AssetAdmin)

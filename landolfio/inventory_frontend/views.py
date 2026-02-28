import json
from datetime import date

from django.conf import settings
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.db.models import Count, Max, OuterRef, Prefetch, Q, Subquery
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse, reverse_lazy
from django.views import View
from django.views.generic import CreateView, DetailView, ListView, TemplateView
from django.views.generic.edit import DeleteView, UpdateView
from django_drf_filepond.api import store_upload
from django_drf_filepond.models import TemporaryUpload

from accounting.models.contact import Contact
from inventory.models.asset import Asset, AssetStates
from inventory.models.asset_property import AssetProperty, AssetPropertyValue
from inventory.models.attachment import Attachment, attachments_directory_path
from inventory.models.category import Category
from inventory.models.collection import Collection
from inventory.models.location import Location
from inventory.models.remarks import Remark
from inventory.models.status_change import StatusChange
from inventory_frontend.forms import AssetForm, BulkStatusChangeForm, StatusChangeForm


def get_locations_hierarchical():
    """Get locations sorted hierarchically by order field recursively."""
    all_locations = list(Location.objects.all())
    location_dict = {loc.id: loc for loc in all_locations}

    # Get ancestry chain order values for sorting
    def get_order_chain(location):
        """Returns tuple of order values from root to this location."""
        chain = []
        current = location
        while current:
            chain.insert(
                0, (current.order if current.order is not None else 999999, current.id)
            )
            if current.parent_id and not current.display_as_root:
                current = location_dict.get(current.parent_id)
            else:
                break
        return tuple(chain)

    # Sort all locations by their ancestry chain
    sorted_locations = sorted(all_locations, key=get_order_chain)
    return sorted_locations


class PublicIndexView(TemplateView):
    template_name = "public_index.html"

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect("inventory_frontend:search")
        return super().dispatch(request, *args, **kwargs)


class AssetSearchView(LoginRequiredMixin, TemplateView):
    template_name = "index.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Get total number of assets
        context["total_assets"] = Asset.objects.count()

        # Get categories with counts and their sizes
        from inventory.models.category import Size

        categories = (
            Category.objects.annotate(asset_count=Count("asset"))
            .filter(asset_count__gt=0)
            .order_by("order", "name")
            .prefetch_related("size_set")
        )

        # Add size information with asset counts for each category
        for category in categories:
            category.sizes_with_counts = []
            for size in category.size_set.all().order_by("order", "name"):
                size_asset_count = Asset.objects.filter(
                    category=category, size=size
                ).count()
                if size_asset_count > 0:
                    category.sizes_with_counts.append(
                        {"size": size, "asset_count": size_asset_count}
                    )

        context["categories"] = categories

        # Get locations marked as display_as_root with their children
        root_locations = (
            Location.objects.filter(display_as_root=True)
            .annotate(asset_count=Count("asset"))
            .order_by("order", "pk")
        )

        # Add child locations with counts for each root location
        for location in root_locations:
            location.children_with_counts = []
            children = (
                Location.objects.filter(
                    parent=location,
                    display_as_root=False,  # Don't show locations that are themselves roots
                )
                .annotate(child_asset_count=Count("asset"))
                .order_by("order", "pk")
            )

            for child in children:
                if child.child_asset_count == 0:
                    continue

                location.children_with_counts.append(
                    {"location": child, "asset_count": child.child_asset_count}
                )

        root_locations = [
            loc
            for loc in root_locations
            if loc.asset_count > 0 or loc.children_with_counts
        ]
        context["locations"] = root_locations

        # Get collections with counts
        context["collections"] = (
            Collection.objects.annotate(asset_count=Count("asset"))
            .filter(asset_count__gt=0)
            .order_by("order", "name")
        )

        return context


class AssetListView(LoginRequiredMixin, ListView):
    template_name = "list.html"
    context_object_name = "assets"
    model = Asset
    paginate_by = 12

    def get_paginate_by(self, queryset):
        """Allow user to specify page size via GET parameter."""
        page_size = self.request.GET.get("page_size", self.paginate_by)
        try:
            page_size = int(page_size)
            # Limit to reasonable values
            if page_size in [12, 24, 48, 96]:
                return page_size
        except (ValueError, TypeError):
            pass
        return self.paginate_by

    def get_queryset(self):
        queryset = super().get_queryset()

        # Get filter parameters (support multiple values)
        search_query = self.request.GET.get("q")
        categories = self.request.GET.getlist("category")
        sizes = self.request.GET.getlist("size")
        statuses = self.request.GET.getlist("status")
        locations = self.request.GET.getlist("location")
        collections = self.request.GET.getlist("collection")
        warnings = self.request.GET.getlist("warning")
        min_value = self.request.GET.get("min_value")
        max_value = self.request.GET.get("max_value")

        # By default, exclude archived statuses unless specific statuses are selected
        # Exception: when searching, include all statuses
        if not statuses and not search_query:
            from inventory.models.status_type import StatusType

            non_archived_statuses = StatusType.objects.filter(
                is_archived=False
            ).values_list("slug", flat=True)

            latest_status = (
                StatusChange.objects.filter(
                    asset=OuterRef("pk"), new_status__isnull=False
                )
                .order_by("-status_date", "-created_at")
                .values("new_status")[:1]
            )

            queryset = queryset.annotate(
                latest_status_from_changes=Subquery(latest_status)
            )

            queryset = queryset.filter(
                Q(latest_status_from_changes__in=non_archived_statuses)
                | Q(
                    latest_status_from_changes__isnull=True,
                    local_status__in=non_archived_statuses,
                )
            )

        # Apply filters
        if search_query and search_query.strip():
            queryset = queryset.filter(
                Q(name__icontains=search_query.strip())
                | Q(category__name__icontains=search_query.strip())
                | Q(remarks__remark__icontains=search_query.strip())
                | Q(tickets__description__icontains=search_query.strip())
                | Q(tickets__contact__first_name__icontains=search_query.strip())
                | Q(tickets__contact__last_name__icontains=search_query.strip())
            )

        if categories:
            # Filter non-empty values
            categories = [cat for cat in categories if cat.strip()]
            if categories:
                queryset = queryset.filter(category_id__in=categories)

        if sizes:
            # Filter non-empty values
            sizes = [size for size in sizes if size.strip()]
            if sizes:
                queryset = queryset.filter(size_id__in=sizes)

        if statuses:
            # Filter non-empty values
            statuses = [stat for stat in statuses if stat.strip()]
            if statuses:
                # Annotate each asset with its latest status from StatusChanges
                latest_status = (
                    StatusChange.objects.filter(
                        asset=OuterRef("pk"), new_status__isnull=False
                    )
                    .order_by("-status_date", "-created_at")
                    .values("new_status")[:1]
                )

                queryset = queryset.annotate(
                    latest_status_from_changes=Subquery(latest_status)
                )

                # Filter where either the latest status change matches OR
                # no status changes exist and local_status matches
                queryset = queryset.filter(
                    Q(latest_status_from_changes__in=statuses)
                    | Q(
                        latest_status_from_changes__isnull=True,
                        local_status__in=statuses,
                    )
                )

        if locations:
            # Filter non-empty values
            locations_ids = [loc for loc in locations if loc.strip()]
            if locations_ids:
                # Include sublocations for each selected location
                all_location_ids = set(locations_ids)
                for loc_id in locations_ids:
                    try:
                        location = Location.objects.get(id=loc_id)
                        # Add all descendant location IDs
                        descendants = location.get_descendants(include_self=False)
                        all_location_ids.update([str(d.id) for d in descendants])
                    except Location.DoesNotExist:
                        pass
                queryset = queryset.filter(location_id__in=all_location_ids)

        if collections:
            # Filter non-empty values
            collections = [col for col in collections if col.strip()]
            if collections:
                queryset = queryset.filter(collection_id__in=collections)

        if min_value and min_value.strip():
            try:
                min_val = float(min_value)
                # Only apply filter if min_value is greater than 0 (not default)
                if min_val > 0:
                    queryset = queryset.filter(listing_price__gte=min_val)
            except (ValueError, TypeError):
                pass

        if max_value and max_value.strip():
            try:
                max_val = float(max_value)
                # Only apply filter if max_value is less than 10000 (not default)
                if max_val < 10000:
                    queryset = queryset.filter(listing_price__lte=max_val)
            except (ValueError, TypeError):
                pass

        # Apply warning filters
        if warnings:
            warnings = [w for w in warnings if w.strip()]

            # Check if we need to add status annotations
            need_status_annotation = "status_mismatch" in warnings

            if need_status_annotation:
                # Annotate with latest status if not already done
                if "latest_status_from_changes" not in queryset.query.annotations:
                    latest_status = (
                        StatusChange.objects.filter(
                            asset=OuterRef("pk"), new_status__isnull=False
                        )
                        .order_by("-status_date", "-created_at")
                        .values("new_status")[:1]
                    )
                    queryset = queryset.annotate(
                        latest_status_from_changes=Subquery(latest_status)
                    )

                # Add effective_status annotation if not already done
                if "effective_status" not in queryset.query.annotations:
                    from django.db.models.functions import Coalesce

                    queryset = queryset.annotate(
                        effective_status=Coalesce(
                            "latest_status_from_changes", "local_status"
                        )
                    )

            # Build warning filters
            warning_filters = Q()
            for warning_type in warnings:
                if warning_type == "status_mismatch":
                    # Filter assets where local status doesn't match financial disposal
                    # Only check for mismatches on assets linked to Moneybird
                    warning_filters |= (
                        (
                            # Local status is sold but disposal is not divested (or no disposal at all)
                            Q(moneybird_asset_id__isnull=False, effective_status="sold")
                            & ~Q(disposal="divested")
                        )
                        | (
                            # Local status is amortized but disposal is not out_of_use (or no disposal at all)
                            Q(
                                moneybird_asset_id__isnull=False,
                                effective_status="amortized",
                            )
                            & ~Q(disposal="out_of_use")
                        )
                        | (
                            # Disposal is divested but local status is not sold
                            Q(disposal="divested")
                            & ~Q(effective_status="sold")
                        )
                        | (
                            # Disposal is out_of_use but local status is not amortized
                            Q(disposal="out_of_use")
                            & ~Q(effective_status="amortized")
                        )
                    )
                elif warning_type == "non_commerce_linked":
                    # Filter non-commerce assets linked to Moneybird and not disposed
                    warning_filters |= Q(
                        collection__commerce=False,
                        moneybird_asset_id__isnull=False,
                        disposal__isnull=True,
                    )
                elif warning_type == "missing_sources":
                    # Filter assets linked to Moneybird with no sources (financially unlinked)
                    # SQLite uses json_array_length, PostgreSQL uses jsonb_array_length
                    # For now, get all linked assets and filter in Python
                    pass  # Will be handled after applying warning_filters
                elif warning_type == "no_photos":
                    # Filter assets with no attachments (no photos)
                    warning_filters |= Q(attachments__isnull=True)

            if warning_filters:
                queryset = queryset.filter(warning_filters)

            # Handle missing_sources separately (requires Python-side filtering for JSON array)
            if "missing_sources" in warnings:
                # Only check assets that are linked to Moneybird
                linked_assets = queryset.filter(moneybird_asset_id__isnull=False)
                asset_ids_with_missing_sources = []

                for asset in linked_assets:
                    # Check if sources is missing, null, or empty array
                    sources = (
                        asset.moneybird_data.get("sources")
                        if asset.moneybird_data
                        else None
                    )
                    if not sources or len(sources) == 0:
                        asset_ids_with_missing_sources.append(asset.id)

                if asset_ids_with_missing_sources:
                    queryset = queryset.filter(id__in=asset_ids_with_missing_sources)
                else:
                    queryset = queryset.none()

        # Apply property filters
        property_filters = self._get_property_filters()
        for property_filter in property_filters:
            queryset = queryset.filter(property_filter)

        # Apply numeric range filters separately
        queryset = self._apply_numeric_range_filters(queryset)

        return queryset.select_related("category", "location", "collection", "size")

    def _apply_numeric_range_filters(self, queryset):
        """Apply numeric range filters using proper numeric comparison."""
        from django.db.models import DecimalField
        from django.db.models.functions import Cast

        for param_name, param_values in self.request.GET.lists():
            if param_name.endswith(("_min", "_max")):
                try:
                    property_slug = param_name.replace("_min", "").replace("_max", "")
                    property_obj = AssetProperty.objects.get(slug=property_slug)

                    if property_obj.property_type == "number":
                        range_type = "min" if param_name.endswith("_min") else "max"

                        for param_value in param_values:
                            if param_value.strip():
                                numeric_value = float(param_value)

                                # Apply range filter using Cast for proper numeric comparison
                                if range_type == "min":
                                    queryset = queryset.filter(
                                        property_values__property=property_obj,
                                        property_values__value__regex=r"^[0-9]+\.?[0-9]*$",
                                    ).extra(
                                        where=[
                                            "CAST(inventory_assetpropertyvalue.value AS DECIMAL(10,2)) >= %s"
                                        ],
                                        params=[numeric_value],
                                    )
                                else:  # max
                                    queryset = queryset.filter(
                                        property_values__property=property_obj,
                                        property_values__value__regex=r"^[0-9]+\.?[0-9]*$",
                                    ).extra(
                                        where=[
                                            "CAST(inventory_assetpropertyvalue.value AS DECIMAL(10,2)) <= %s"
                                        ],
                                        params=[numeric_value],
                                    )
                                break
                except (ValueError, TypeError, AssetProperty.DoesNotExist):
                    continue

        return queryset

    def _parse_property_parameters(self):
        """Parse property-related parameters from the request."""
        property_params = {}

        for param_name, param_values in self.request.GET.lists():
            try:
                if param_name.endswith(("_min", "_max")):
                    self._handle_numeric_property_param(
                        param_name, param_values, property_params
                    )
                else:
                    self._handle_property_param(
                        param_name, param_values, property_params
                    )
            except (ValueError, TypeError, AssetProperty.DoesNotExist):
                continue

        return property_params

    def _handle_numeric_property_param(self, param_name, param_values, property_params):
        """Handle numeric property range parameters (min/max)."""
        property_slug = param_name.replace("_min", "").replace("_max", "")
        range_type = "min" if param_name.endswith("_min") else "max"

        property_obj = AssetProperty.objects.get(slug=property_slug)
        property_id = property_obj.id

        if property_id not in property_params:
            property_params[property_id] = {"type": "number", "obj": property_obj}

        for param_value in param_values:
            if param_value.strip():
                property_params[property_id][range_type] = float(param_value)
                break

    def _handle_property_param(self, param_name, param_values, property_params):
        """Handle string and dropdown property parameters."""
        property_obj = AssetProperty.objects.get(slug=param_name)
        property_id = property_obj.id

        non_empty_values = [v for v in param_values if v.strip()]
        if non_empty_values:
            property_params[property_id] = {
                "type": property_obj.property_type,
                "values": non_empty_values,
                "obj": property_obj,
            }

    def _build_property_filters(self, property_params):
        """Build Django Q objects for property filtering."""
        filters = []

        for property_id, params in property_params.items():
            property_type = params["type"]

            if property_type == "number":
                filter_q = self._build_numeric_filter(property_id, params)
            elif property_type == "dropdown":
                filter_q = self._build_dropdown_filter(property_id, params)
            else:  # string
                filter_q = self._build_string_filter(property_id, params)

            if filter_q:
                filters.append(filter_q)

        return filters

    def _build_numeric_filter(self, property_id, params):
        """Build filter for numeric properties."""
        has_min = "min" in params
        has_max = "max" in params

        if not (has_min or has_max):
            return None

        # Base filter for valid numeric values
        base_filter = (
            Q(property_values__property_id=property_id)
            & Q(property_values__value__regex=r"^[0-9]+\.?[0-9]*$")
            & ~Q(property_values__value="")
        )

        # For range filtering, we need to do post-processing since we store numeric values as strings
        # We'll return the base filter and let the get_queryset method handle the range logic
        return base_filter

    def _build_dropdown_filter(self, property_id, params):
        """Build filter for dropdown properties."""
        values = params.get("values", [])
        if not values:
            return None

        value_filters = Q()
        for value in values:
            value_filters |= Q(property_values__value__exact=value)

        return Q(property_values__property_id=property_id) & value_filters

    def _build_string_filter(self, property_id, params):
        """Build filter for string properties."""
        values = params.get("values", [])
        if not values:
            return None

        return Q(property_values__property_id=property_id) & Q(
            property_values__value__icontains=values[0]
        )

    def _get_property_filters(self):
        """Extract and build property filter conditions from request parameters."""
        property_params = self._parse_property_parameters()
        return self._build_property_filters(property_params)

    def _get_properties_with_current_values(self):
        """Get all properties with their current filter values attached."""
        properties = AssetProperty.objects.prefetch_related("categories").order_by(
            "name", "order"
        )

        for prop in properties:
            prop.current_values = self.request.GET.getlist(prop.slug)

            # For numeric properties, also add min/max values
            if prop.property_type == "number":
                prop.current_min = self.request.GET.get(f"{prop.slug}_min", "")
                prop.current_max = self.request.GET.get(f"{prop.slug}_max", "")

        return properties

    def _parse_property_filters_for_display(self):
        """Parse property filters for display in context."""
        property_filters = {}

        for param_name, param_value in self.request.GET.items():
            if not param_value.strip():
                continue

            try:
                property_obj = self._get_property_from_param(param_name)
                if property_obj:
                    self._add_display_filter(
                        property_filters, param_name, param_value, property_obj
                    )
            except AssetProperty.DoesNotExist:
                continue

        return property_filters

    def _get_property_from_param(self, param_name):
        """Extract property object from parameter name."""
        if param_name.endswith(("_min", "_max")):
            property_slug = param_name.replace("_min", "").replace("_max", "")
            return AssetProperty.objects.get(slug=property_slug)
        else:
            return AssetProperty.objects.get(slug=param_name)

    def _add_display_filter(
        self, property_filters, param_name, param_value, property_obj
    ):
        """Add filter to display filters dictionary."""
        property_id = property_obj.id

        if param_name.endswith(("_min", "_max")):
            range_type = "min" if param_name.endswith("_min") else "max"
            if property_id not in property_filters:
                property_filters[property_id] = {}
            property_filters[property_id][range_type] = param_value
        else:
            property_filters[property_id] = param_value

    def _count_active_property_filters(self):
        """Count the number of active property filters."""
        count = 0

        for key, value in self.request.GET.items():
            if not value.strip():
                continue

            try:
                # Check if it's a direct property slug
                AssetProperty.objects.get(slug=key)
                count += 1
            except AssetProperty.DoesNotExist:
                # Check if it's a min/max parameter
                if key.endswith(("_min", "_max")):
                    property_slug = key.replace("_min", "").replace("_max", "")
                    try:
                        AssetProperty.objects.get(slug=property_slug)
                        count += 1
                    except AssetProperty.DoesNotExist:
                        pass

        return count

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Get base queryset for filtered counts
        base_qs = self.get_queryset()

        # Get categories with counts
        context["categories"] = Category.objects.annotate(
            asset_count=Count("asset")
        ).order_by("name")

        # Get sizes with counts
        from inventory.models.category import Size

        context["sizes"] = Size.objects.annotate(asset_count=Count("asset")).order_by(
            "order", "name"
        )

        # Get hierarchical locations with counts
        from django.db.models import Prefetch, Q

        # Get all locations with their asset counts
        all_locations = Location.objects.annotate(asset_count=Count("asset")).order_by(
            "order", "pk"
        )

        # Build hierarchical structure
        # Get root locations (no parent or display_as_root=True)
        root_locations = all_locations.filter(
            Q(parent__isnull=True) | Q(display_as_root=True)
        )

        # Build full tree for each root location
        def build_tree(location, all_locs):
            """Recursively build the full location tree."""
            children = [loc for loc in all_locs if loc.parent_id == location.id]
            location.children_list = []
            total_count = location.asset_count

            for child in children:
                build_tree(child, all_locs)
                location.children_list.append(child)
                total_count += child.total_asset_count

            location.total_asset_count = total_count

        all_locs_list = list(all_locations)
        for root in root_locations:
            build_tree(root, all_locs_list)

        context["location_groups"] = root_locations

        # Get collections with counts
        context["collections"] = Collection.objects.annotate(
            asset_count=Count("asset")
        ).order_by("name")

        # Get status types and separate into active and archived
        from inventory.models.status_type import StatusType

        all_status_types = StatusType.objects.order_by("order", "name")
        active_status_types = all_status_types.filter(is_archived=False)
        archived_status_types = all_status_types.filter(is_archived=True)

        context["active_status_types"] = active_status_types
        context["archived_status_types"] = archived_status_types

        # Determine which statuses are effectively active
        selected_statuses = self.request.GET.getlist("status")
        search_query = self.request.GET.get("q", "").strip()

        if selected_statuses:
            # If specific statuses are selected, use those
            effective_statuses = selected_statuses
            status_filter_modified = True
        elif search_query:
            # When searching, all statuses are included
            effective_statuses = [s.slug for s in all_status_types]
            status_filter_modified = False
        else:
            # By default, only non-archived statuses are included
            effective_statuses = [s.slug for s in active_status_types]
            status_filter_modified = False

        context["effective_statuses"] = effective_statuses
        context["status_filter_modified"] = status_filter_modified

        # Get all properties for the filter dropdown with current values
        context["all_properties"] = self._get_properties_with_current_values()

        # Parse property filters for display
        property_filters = self._parse_property_filters_for_display()
        property_filter_count = self._count_active_property_filters()

        # Add current filter values
        context["current_filters"] = {
            "q": self.request.GET.get("q", ""),
            "categories": self.request.GET.getlist("category"),
            "sizes": self.request.GET.getlist("size"),
            "statuses": self.request.GET.getlist("status"),
            "locations": self.request.GET.getlist("location"),
            "collections": self.request.GET.getlist("collection"),
            "warnings": self.request.GET.getlist("warning"),
            "min_value": self.request.GET.get("min_value", ""),
            "max_value": self.request.GET.get("max_value", ""),
            "properties": property_filters,
            "property_count": property_filter_count,
        }

        return context


class AssetDetailView(LoginRequiredMixin, DetailView):
    template_name = "detail.html"
    model = Asset
    context_object_name = "asset"

    def get_queryset(self):
        return (
            super()
            .get_queryset()
            .select_related("category", "location", "collection", "size")
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        asset = self.object

        # Refresh from Moneybird if linked
        if asset.moneybird_asset_id:
            try:
                asset.refresh_from_moneybird()
            except Exception as e:
                messages.warning(
                    self.request,
                    f"Failed to refresh asset data from Moneybird: {str(e)}",
                )

        # Add financial data
        context["financial_data"] = {
            "purchase_value": asset.purchase_value_asset,
        }

        # Add status information
        context["is_disposed"] = asset.is_disposed
        context["disposal_reason"] = asset.disposal_reason_display

        # Add status change form
        context["status_change_form"] = StatusChangeForm(asset=asset)

        # Add form data for status update in logical color grouping order
        context["asset_states"] = [
            # Green - Available
            (AssetStates.AVAILABLE, AssetStates.AVAILABLE.label),
            # Blue - Maintenance/Review
            (AssetStates.UNDER_REVIEW, AssetStates.UNDER_REVIEW.label),
            (AssetStates.MAINTENANCE_IN_HOUSE, AssetStates.MAINTENANCE_IN_HOUSE.label),
            (AssetStates.MAINTENANCE_EXTERNAL, AssetStates.MAINTENANCE_EXTERNAL.label),
            # Yellow - Active/Issued
            (AssetStates.ISSUED_UNPROCESSED, AssetStates.ISSUED_UNPROCESSED.label),
            (AssetStates.ISSUED_LOAN, AssetStates.ISSUED_LOAN.label),
            (AssetStates.ISSUED_RENT, AssetStates.ISSUED_RENT.label),
            # Dark - Final/Completed
            (AssetStates.SOLD, AssetStates.SOLD.label),
            (AssetStates.AMORTIZED, AssetStates.AMORTIZED.label),
            # Red - Problem
            (AssetStates.UNKNOWN, AssetStates.UNKNOWN.label),
            # Gray - Placeholder/Pending
            (AssetStates.PLACEHOLDER, AssetStates.PLACEHOLDER.label),
            (AssetStates.TO_BE_DELIVERED, AssetStates.TO_BE_DELIVERED.label),
        ]
        context["locations"] = get_locations_hierarchical()

        context["journal_history"] = []

        # Add asset properties
        category_properties = AssetProperty.objects.filter(
            categories=asset.category
        ).order_by("order", "name")

        # Get existing property values for this asset
        existing_values = {
            pv.property_id: pv
            for pv in AssetPropertyValue.objects.filter(asset=asset).select_related(
                "property"
            )
        }

        # Create a list of properties with their current values
        properties_with_values = []
        for prop in category_properties:
            value_obj = existing_values.get(prop.id)
            properties_with_values.append(
                {
                    "property": prop,
                    "value_obj": value_obj,
                    "current_value": value_obj.value if value_obj else "",
                    "formatted_value": (
                        value_obj.get_formatted_value() if value_obj else ""
                    ),
                }
            )

        context["asset_properties"] = properties_with_values

        # Build back URL to list view with preserved parameters
        back_url = reverse("inventory_frontend:list")
        referer = self.request.META.get("HTTP_REFERER", "")

        # If coming from list view, preserve the query parameters
        if "/list/" in referer and "?" in referer:
            query_params = referer.split("?", 1)[1]
            back_url += "?" + query_params

        context["back_url"] = back_url

        return context

    def post(self, request, *args, **kwargs):
        asset = self.get_object()
        data = request.POST

        # Handle remark creation
        if data.get("action") == "add_remark":
            new_remark = data.get("new_remark", "").strip()
            if new_remark:
                Remark.objects.create(asset=asset, remark=new_remark)
                messages.success(request, "Remark added successfully")
            else:
                messages.error(request, "Please enter a remark")
            return redirect(request.path)

        # Handle remark deletion
        if data.get("action") == "delete_remark":
            remark_id = data.get("remark_id")
            if remark_id:
                try:
                    remark = Remark.objects.get(id=remark_id, asset=asset)
                    remark.delete()
                    messages.success(request, "Remark deleted successfully")
                except Remark.DoesNotExist:
                    messages.error(request, "Remark not found")
            else:
                messages.error(request, "Invalid remark ID")
            return redirect(request.path)

        # Handle status change creation
        if data.get("action") == "create_status_change":
            form = StatusChangeForm(data, asset=asset)
            if form.is_valid():
                status_change = form.save()

                # Handle Moneybird synchronization for sold/amortized statuses
                sync_to_moneybird = data.get("sync_to_moneybird") == "true"
                new_status = form.cleaned_data.get("new_status")

                if (
                    sync_to_moneybird
                    and asset.moneybird_asset_id
                    and new_status in ["sold", "amortized"]
                ):
                    try:
                        from datetime import date
                        from inventory.moneybird import MoneybirdAssetService

                        service = MoneybirdAssetService()

                        # Use the status change date or today's date
                        status_date = (
                            form.cleaned_data.get("status_date") or date.today()
                        )
                        status_date_str = status_date.strftime("%Y-%m-%d")

                        # Get comments from the form
                        comments = form.cleaned_data.get("comments", "").strip()

                        if new_status == "sold":
                            # For sold: create divestment value change (automatically disposes as divested)
                            description = "Verkocht"
                            if comments:
                                description = f"Verkocht - {comments}"
                            service.create_divestment_value_change(
                                asset.moneybird_asset_id, status_date_str, description
                            )
                            messages.success(
                                request,
                                "Status change created and synced to Moneybird as divested",
                            )
                        else:  # amortized
                            # For amortized: fully depreciate (automatically disposes as out_of_use)
                            description = "Afgeschreven"
                            if comments:
                                description = f"Afgeschreven - {comments}"
                            service.fully_depreciate_asset(
                                asset.moneybird_asset_id, status_date_str, description
                            )
                            messages.success(
                                request,
                                "Status change created and synced to Moneybird as out of use",
                            )
                    except Exception as e:
                        messages.error(
                            request, f"Failed to sync to Moneybird: {str(e)}"
                        )
                else:
                    messages.success(request, "Status change created successfully")
            else:
                for field, errors in form.errors.items():
                    for error in errors:
                        messages.error(request, f"{field}: {error}")
            return redirect(request.path)

        # Handle status change deletion
        if data.get("action") == "delete_status_change":
            status_change_id = data.get("status_change_id")
            if status_change_id:
                try:
                    status_change = StatusChange.objects.get(
                        id=status_change_id, asset=asset
                    )
                    status_change.delete()
                    messages.success(request, "Status change deleted successfully")
                except StatusChange.DoesNotExist:
                    messages.error(request, "Status change not found")
            else:
                messages.error(request, "Invalid status change ID")
            return redirect(request.path)

        # Handle unified form updates (status, location, listing price, and properties)
        if data.get("action") in ["update_status", "update_all"]:
            updated_items = []

            # Update location
            new_location_id = data.get("new_location", "").strip()
            if new_location_id:
                try:
                    new_location = Location.objects.get(pk=new_location_id)
                    if new_location != asset.location:
                        asset.location = new_location
                        updated_items.append("location")
                except Location.DoesNotExist:
                    messages.error(request, "Invalid location selected")
                    return redirect(request.path)

            # Update location number
            new_location_nr = data.get("new_location_nr", "").strip()
            if new_location_nr:
                try:
                    new_location_nr_int = int(new_location_nr)
                    if new_location_nr_int != asset.location_nr:
                        asset.location_nr = new_location_nr_int
                        updated_items.append("location number")
                except ValueError:
                    messages.error(request, "Invalid location number")
                    return redirect(request.path)
            elif new_location_nr == "" and asset.location_nr is not None:
                # Clear location number if empty string provided
                asset.location_nr = None
                updated_items.append("location number (cleared)")

            # Update listing price
            listing_price = data.get("listing_price", "").strip()
            if listing_price:
                try:
                    new_listing_price = float(listing_price)
                    if new_listing_price != (asset.listing_price or 0):
                        asset.listing_price = new_listing_price
                        updated_items.append("listing price")
                except ValueError:
                    messages.error(request, "Invalid listing price")
                    return redirect(request.path)
            elif listing_price == "" and asset.listing_price is not None:
                # Clear listing price if empty string provided
                asset.listing_price = None
                updated_items.append("listing price (cleared)")

            # Handle property updates
            updated_properties = self._update_asset_properties(asset, data)
            updated_items.extend(updated_properties)

            # Save asset changes
            asset.save()

            # Show success message
            if updated_items:
                messages.success(
                    request, f"Updated {', '.join(updated_items)} successfully"
                )
            else:
                messages.info(request, "No changes made")

            return redirect(request.path)

        # Handle file uploads
        try:
            filepond_ids = data.getlist("filepond")
        except KeyError:
            filepond_ids = []

        if not isinstance(filepond_ids, list):
            filepond_ids = []

        stored_uploads = []
        for upload_id in filepond_ids:
            if upload_id == "":
                continue

            try:
                tu = TemporaryUpload.objects.get(upload_id=upload_id)
            except TemporaryUpload.DoesNotExist:
                messages.error(request, f"Upload with id {upload_id} does not exist")
                continue

            # Get the next order value for this asset
            max_order = asset.attachments.aggregate(Max("order"))["order__max"] or 0

            attachment = Attachment(asset=asset, order=max_order + 1)
            stored_upload = store_upload(
                upload_id, attachments_directory_path(attachment, tu.upload_name)
            )
            attachment.attachment = stored_upload.file
            attachment.save()
            stored_uploads.append(upload_id)

        if stored_uploads:
            messages.success(
                request, f"Successfully uploaded {len(stored_uploads)} files"
            )

        return redirect(request.path)

    def _update_asset_properties(self, asset, data):
        """Update asset property values from form data."""
        updated_properties = []
        category_properties = AssetProperty.objects.filter(categories=asset.category)

        for prop in category_properties:
            field_name = f"property_{prop.slug}"
            new_value = data.get(field_name, "").strip()

            if new_value:
                updated_properties.extend(
                    self._set_property_value(asset, prop, new_value)
                )
            else:
                updated_properties.extend(self._clear_property_value(asset, prop))

        return updated_properties

    def _set_property_value(self, asset, prop, new_value):
        """Set or update a property value for an asset."""
        property_value, created = AssetPropertyValue.objects.get_or_create(
            asset=asset, property=prop, defaults={"value": new_value}
        )

        if created:
            return [prop.name]
        elif property_value.value != new_value:
            property_value.value = new_value
            property_value.save()
            return [prop.name]

        return []

    def _clear_property_value(self, asset, prop):
        """Clear/delete a property value for an asset."""
        try:
            property_value = AssetPropertyValue.objects.get(asset=asset, property=prop)
            property_value.delete()
            return [f"{prop.name} (cleared)"]
        except AssetPropertyValue.DoesNotExist:
            return []


class AssetCreateView(LoginRequiredMixin, CreateView):
    template_name = "create.html"
    model = Asset
    form_class = AssetForm
    success_url = reverse_lazy("inventory_frontend:list")

    def form_valid(self, form):
        # Default values are now handled in the form's __init__ method
        response = super().form_valid(form)

        # Create initial status change for new asset
        asset = self.object
        asset.create_status_change(
            new_status=AssetStates.PLACEHOLDER,
            status_date=asset.start_date if asset.start_date else date.today(),
            comments="Initial status for new asset",
        )

        # Try to create on Moneybird if required fields are present
        if (
            settings.AUTO_CREATE_ASSET_ON_MONEYBIRD
            and asset.start_date
            and asset.purchase_value_asset
        ):
            try:
                asset.create_on_moneybird()
                messages.success(
                    self.request,
                    f'Asset "{asset.name}" created successfully and pushed to Moneybird.',
                )
            except Exception as e:
                messages.warning(
                    self.request,
                    f'Asset "{asset.name}" created successfully, but failed to push to Moneybird: {str(e)}',
                )
        else:
            messages.success(
                self.request,
                f'Asset "{asset.name}" created successfully. Add start date and purchase value to sync with Moneybird.',
            )

        return response

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["categories"] = Category.objects.all()
        context["locations"] = get_locations_hierarchical()
        context["collections"] = Collection.objects.all()
        return context


class AssetUpdateView(LoginRequiredMixin, SuccessMessageMixin, UpdateView):
    model = Asset
    form_class = AssetForm
    template_name = "update.html"
    success_message = "Asset was updated successfully"

    def form_valid(self, form):
        original_asset = Asset.objects.get(pk=self.object.pk)
        response = super().form_valid(form)

        # If asset is linked to Moneybird and name changed, update Moneybird
        if self.object.moneybird_asset_id:
            # Only track name changes - financial fields are readonly when linked
            if original_asset.name != self.object.name:
                try:
                    self.object.update_on_moneybird()
                    messages.success(
                        self.request,
                        "Asset updated successfully and synchronized with Moneybird",
                    )
                except Exception as e:
                    messages.warning(
                        self.request,
                        f"Asset updated successfully, but failed to sync with Moneybird: {str(e)}",
                    )

        return response

    def get_success_url(self):
        return reverse_lazy("inventory_frontend:detail", kwargs={"pk": self.object.pk})


class AssetDeleteView(LoginRequiredMixin, PermissionRequiredMixin, DeleteView):
    model = Asset
    permission_required = "inventory.delete_asset"
    success_url = reverse_lazy("inventory_frontend:list")

    def get_success_url(self):
        messages.success(self.request, f'Asset "{self.object.name}" has been deleted.')
        return super().get_success_url()


class AssetAutocompleteView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        query = request.GET.get("q", "").strip()

        if len(query) < 2:
            return JsonResponse([], safe=False)

        assets = (
            Asset.objects.filter(name__icontains=query)
            .select_related("category", "size", "location")
            .distinct()[:10]
        )

        suggestions = []
        for asset in assets:
            suggestions.append(
                {
                    "id": str(asset.id),
                    "name": asset.name,
                    "category": (
                        asset.category.name_singular if asset.category else None
                    ),
                    "size": str(asset.size) if asset.size else None,
                    "location": str(asset.location) if asset.location else None,
                    "location_nr": asset.location_nr,
                    "created_at": (
                        asset.created_at.strftime("%d-%m-%Y")
                        if asset.created_at
                        else None
                    ),
                    "purchase_value": (
                        float(asset.purchase_value_asset)
                        if asset.purchase_value_asset
                        else 0
                    ),
                    "listing_price": (
                        float(asset.listing_price) if asset.listing_price else 0
                    ),
                    "is_disposed": asset.is_disposed,
                    "disposal_reason": asset.disposal_reason_display,
                    "current_status": asset.current_status,
                    "current_status_display": asset.current_status_display,
                }
            )

        return JsonResponse(suggestions, safe=False)


class PropertyValueAutocompleteView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        query = request.GET.get("query", request.GET.get("q", "")).strip()
        property_id = request.GET.get("property_id", "").strip()

        if len(query) < 1 or not property_id:
            return JsonResponse([], safe=False)

        try:
            property_obj = AssetProperty.objects.get(slug=property_id)
        except AssetProperty.DoesNotExist:
            return JsonResponse([], safe=False)

        # Get distinct values for this property from assets in categories that use this property
        values = (
            AssetPropertyValue.objects.filter(
                property=property_obj,
                asset__category__in=property_obj.categories.all(),  # Only from categories that use this property
                value__icontains=query,
            )
            .values_list("value", flat=True)
            .distinct()
            .order_by("value")[:10]
        )

        suggestions = [{"value": value} for value in values if value]

        return JsonResponse(suggestions, safe=False)


class ContactAutocompleteView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        query = request.GET.get("query", request.GET.get("q", "")).strip()

        if len(query) < 2:
            return JsonResponse([], safe=False)

        contacts = Contact.objects.filter(
            Q(company_name__icontains=query)
            | Q(first_name__icontains=query)
            | Q(last_name__icontains=query)
        ).distinct()[:10]

        suggestions = []
        for contact in contacts:
            display_name = str(contact)  # Uses the __str__ method
            suggestions.append(
                {
                    "id": contact.id,
                    "name": display_name,
                    "company_name": contact.company_name or "",
                    "first_name": contact.first_name or "",
                    "last_name": contact.last_name or "",
                }
            )

        return JsonResponse(suggestions, safe=False)


class AttachmentDeleteView(LoginRequiredMixin, View):
    def post(self, request, asset_pk, attachment_pk):
        asset = get_object_or_404(Asset, pk=asset_pk)
        attachment = get_object_or_404(Attachment, pk=attachment_pk, asset=asset)

        try:
            attachment.delete()
            messages.success(request, "Attachment deleted successfully")
        except Exception as e:
            messages.error(request, f"Error deleting attachment: {str(e)}")

        return JsonResponse({"success": True})


class AttachmentReorderView(LoginRequiredMixin, View):
    def post(self, request, asset_pk):
        asset = get_object_or_404(Asset, pk=asset_pk)

        try:
            data = json.loads(request.body)
            attachment_ids = data.get("attachment_ids", [])

            # Update the order of each attachment
            for index, attachment_id in enumerate(attachment_ids):
                try:
                    attachment = Attachment.objects.get(pk=attachment_id, asset=asset)
                    attachment.order = index
                    attachment.save()
                except Attachment.DoesNotExist:
                    continue

            return JsonResponse({"success": True})

        except Exception as e:
            messages.error(request, f"Error reordering attachments: {str(e)}")
            return JsonResponse({"success": False, "error": str(e)})


class AttachmentDownloadView(LoginRequiredMixin, View):
    def get(self, request, asset_pk, attachment_pk):
        from django.http import FileResponse

        asset = get_object_or_404(Asset, pk=asset_pk)
        attachment = get_object_or_404(Attachment, pk=attachment_pk, asset=asset)

        try:
            file_handle = attachment.attachment.open("rb")
            response = FileResponse(
                file_handle, as_attachment=True, filename=attachment.filename
            )
            return response
        except Exception as e:
            return JsonResponse({"success": False, "error": str(e)}, status=500)


class AttachmentDownloadZipView(LoginRequiredMixin, View):
    def post(self, request, asset_pk):
        import io
        import os
        import zipfile

        from django.http import HttpResponse

        asset = get_object_or_404(Asset, pk=asset_pk)

        try:
            data = json.loads(request.body)
            attachment_ids = data.get("attachment_ids", [])

            if not attachment_ids:
                return JsonResponse(
                    {"success": False, "error": "No attachments selected"}
                )

            if len(attachment_ids) == 1:
                attachment = get_object_or_404(
                    Attachment, pk=attachment_ids[0], asset=asset
                )
                file_handle = attachment.attachment.open("rb")
                response = FileResponse(
                    file_handle, as_attachment=True, filename=attachment.filename
                )
                return response

            zip_buffer = io.BytesIO()

            with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zip_file:
                for attachment_id in attachment_ids:
                    try:
                        attachment = Attachment.objects.get(
                            pk=attachment_id, asset=asset
                        )
                        filename = os.path.basename(attachment.attachment.name)
                        with attachment.attachment.open("rb") as f:
                            zip_file.writestr(filename, f.read())
                    except (Attachment.DoesNotExist, FileNotFoundError):
                        continue

            zip_buffer.seek(0)
            response = HttpResponse(
                zip_buffer.getvalue(), content_type="application/zip"
            )
            response["Content-Disposition"] = (
                f'attachment; filename="{asset.name}_attachments.zip"'
            )

            return response

        except Exception as e:
            return JsonResponse({"success": False, "error": str(e)})


class AssetCreateMoneybirdView(LoginRequiredMixin, View):
    def post(self, request, pk):
        asset = get_object_or_404(Asset, pk=pk)

        # Check if asset is already linked to Moneybird
        if asset.moneybird_asset_id:
            messages.warning(
                request, f'Asset "{asset.name}" is already linked to Moneybird.'
            )
            return redirect(
                request.META.get("HTTP_REFERER", reverse("inventory_frontend:list"))
            )

        # Check if required fields are present
        if not asset.start_date or not asset.purchase_value_asset:
            messages.error(
                request,
                f'Asset "{asset.name}" is missing required fields (start date and purchase value) for Moneybird creation.',
            )
            return redirect(
                request.META.get("HTTP_REFERER", reverse("inventory_frontend:list"))
            )

        try:
            asset.create_on_moneybird()
            messages.success(
                request,
                f'Asset "{asset.name}" has been successfully created on Moneybird.',
            )
        except Exception as e:
            messages.error(
                request, f'Failed to create asset "{asset.name}" on Moneybird: {str(e)}'
            )

        return redirect(
            request.META.get("HTTP_REFERER", reverse("inventory_frontend:list"))
        )


class AssetLinkMoneybirdView(LoginRequiredMixin, View):
    def post(self, request, pk):
        asset = get_object_or_404(Asset, pk=pk)

        # Check if asset is already linked to Moneybird
        if asset.moneybird_asset_id:
            messages.warning(
                request, f'Asset "{asset.name}" is already linked to Moneybird.'
            )
            return redirect(
                request.META.get(
                    "HTTP_REFERER",
                    reverse("inventory_frontend:detail", kwargs={"pk": pk}),
                )
            )

        # Get the Moneybird asset ID from form
        moneybird_asset_id = request.POST.get("moneybird_asset_id")
        if not moneybird_asset_id:
            messages.error(request, "Please provide a valid Moneybird Asset ID.")
            return redirect(
                request.META.get(
                    "HTTP_REFERER",
                    reverse("inventory_frontend:detail", kwargs={"pk": pk}),
                )
            )

        try:
            # Convert to integer and validate
            moneybird_asset_id = int(moneybird_asset_id)

            # Check if this Moneybird ID is already linked to another asset
            existing_asset = Asset.objects.filter(
                moneybird_asset_id=moneybird_asset_id
            ).first()
            if existing_asset and existing_asset != asset:
                messages.error(
                    request,
                    f'Moneybird Asset ID {moneybird_asset_id} is already linked to asset "{existing_asset.name}".',
                )
                return redirect(
                    request.META.get(
                        "HTTP_REFERER",
                        reverse("inventory_frontend:detail", kwargs={"pk": pk}),
                    )
                )

            # Link the asset
            asset.moneybird_asset_id = moneybird_asset_id
            asset.save(update_fields=["moneybird_asset_id"])

            # Try to refresh data from Moneybird
            try:
                asset.refresh_from_moneybird()
                messages.success(
                    request,
                    f'Asset "{asset.name}" has been successfully linked to Moneybird Asset {moneybird_asset_id} and data has been refreshed.',
                )
            except Exception as refresh_error:
                messages.warning(
                    request,
                    f'Asset "{asset.name}" has been linked to Moneybird Asset {moneybird_asset_id}, but failed to refresh data: {str(refresh_error)}',
                )

        except ValueError:
            messages.error(
                request, "Please provide a valid numeric Moneybird Asset ID."
            )
        except Exception as e:
            messages.error(
                request, f'Failed to link asset "{asset.name}" to Moneybird: {str(e)}'
            )

        return redirect(
            request.META.get(
                "HTTP_REFERER", reverse("inventory_frontend:detail", kwargs={"pk": pk})
            )
        )


class AssetUnlinkMoneybirdView(LoginRequiredMixin, View):
    def post(self, request, pk):
        asset = get_object_or_404(Asset, pk=pk)

        # Check if asset is linked to Moneybird
        if not asset.moneybird_asset_id:
            messages.warning(
                request, f'Asset "{asset.name}" is not linked to Moneybird.'
            )
            return redirect(
                request.META.get(
                    "HTTP_REFERER",
                    reverse("inventory_frontend:detail", kwargs={"pk": pk}),
                )
            )

        try:
            old_moneybird_id = asset.moneybird_asset_id
            asset.moneybird_asset_id = None
            asset.moneybird_data = None
            asset.save(update_fields=["moneybird_asset_id", "moneybird_data"])
            messages.success(
                request,
                f'Asset "{asset.name}" has been unlinked from Moneybird Asset {old_moneybird_id}.',
            )
        except Exception as e:
            messages.error(
                request,
                f'Failed to unlink asset "{asset.name}" from Moneybird: {str(e)}',
            )

        return redirect(
            request.META.get(
                "HTTP_REFERER", reverse("inventory_frontend:detail", kwargs={"pk": pk})
            )
        )


class AssetDeleteMoneybirdView(LoginRequiredMixin, View):
    def post(self, request, pk):
        asset = get_object_or_404(Asset, pk=pk)

        # Check if asset is linked to Moneybird
        if not asset.moneybird_asset_id:
            messages.warning(
                request, f'Asset "{asset.name}" is not linked to Moneybird.'
            )
            return redirect(
                request.META.get(
                    "HTTP_REFERER",
                    reverse("inventory_frontend:detail", kwargs={"pk": pk}),
                )
            )

        try:
            old_moneybird_name = asset.moneybird_asset_name
            asset.delete_from_moneybird()
            messages.success(
                request,
                f'Asset "{old_moneybird_name}" has been successfully deleted from Moneybird and unlinked.',
            )
        except Exception as e:
            messages.error(
                request,
                f'Failed to delete asset "{asset.name}" from Moneybird: {str(e)}',
            )

        return redirect(
            request.META.get(
                "HTTP_REFERER", reverse("inventory_frontend:detail", kwargs={"pk": pk})
            )
        )


class AssetRefreshMoneybirdView(LoginRequiredMixin, View):
    def post(self, request, pk):
        asset = get_object_or_404(Asset, pk=pk)

        # Check if asset is linked to Moneybird
        if not asset.moneybird_asset_id:
            messages.warning(
                request, f'Asset "{asset.name}" is not linked to Moneybird.'
            )
            return redirect(
                request.META.get(
                    "HTTP_REFERER",
                    reverse("inventory_frontend:detail", kwargs={"pk": pk}),
                )
            )

        try:
            asset.refresh_from_moneybird()
            messages.success(
                request,
                f'Asset "{asset.name}" has been successfully refreshed from Moneybird.',
            )
        except Exception as e:
            messages.error(
                request,
                f'Failed to refresh asset "{asset.name}" from Moneybird: {str(e)}',
            )

        return redirect(
            request.META.get(
                "HTTP_REFERER", reverse("inventory_frontend:detail", kwargs={"pk": pk})
            )
        )


class AssetUpdateMoneybirdView(LoginRequiredMixin, View):
    def post(self, request, pk):
        asset = get_object_or_404(Asset, pk=pk)

        # Check if asset is linked to Moneybird
        if not asset.moneybird_asset_id:
            messages.warning(
                request, f'Asset "{asset.name}" is not linked to Moneybird.'
            )
            return redirect(
                request.META.get(
                    "HTTP_REFERER",
                    reverse("inventory_frontend:detail", kwargs={"pk": pk}),
                )
            )

        try:
            asset.update_on_moneybird()
            messages.success(
                request,
                f'Asset "{asset.name}" has been successfully updated on Moneybird with current local data.',
            )
        except Exception as e:
            messages.error(
                request, f'Failed to update asset "{asset.name}" on Moneybird: {str(e)}'
            )

        return redirect(
            request.META.get(
                "HTTP_REFERER", reverse("inventory_frontend:detail", kwargs={"pk": pk})
            )
        )


class AssetDisposeMoneybirdView(LoginRequiredMixin, View):
    def post(self, request, pk):
        asset = get_object_or_404(Asset, pk=pk)

        # Check if asset is linked to Moneybird
        if not asset.moneybird_asset_id:
            messages.warning(
                request, f'Asset "{asset.name}" is not linked to Moneybird.'
            )
            return redirect(
                request.META.get(
                    "HTTP_REFERER",
                    reverse("inventory_frontend:detail", kwargs={"pk": pk}),
                )
            )

        # Check if asset is already disposed
        if asset.is_disposed:
            messages.warning(request, f'Asset "{asset.name}" is already disposed.')
            return redirect(
                request.META.get(
                    "HTTP_REFERER",
                    reverse("inventory_frontend:detail", kwargs={"pk": pk}),
                )
            )

        # Get disposal reason from form
        disposal_reason = request.POST.get("disposal_reason")
        if not disposal_reason or disposal_reason not in [
            "out_of_use",
            "divested",
        ]:
            messages.error(request, "Invalid disposal reason.")
            return redirect(
                request.META.get(
                    "HTTP_REFERER",
                    reverse("inventory_frontend:detail", kwargs={"pk": pk}),
                )
            )

        # Get disposal date from form
        disposal_date_str = request.POST.get("disposal_date")
        if not disposal_date_str:
            messages.error(request, "Disposal date is required.")
            return redirect(
                request.META.get(
                    "HTTP_REFERER",
                    reverse("inventory_frontend:detail", kwargs={"pk": pk}),
                )
            )

        try:
            from datetime import datetime

            disposal_date = datetime.strptime(disposal_date_str, "%Y-%m-%d").date()

            if disposal_reason == "divested":
                # For divested, use divestment value change which automatically creates disposal
                asset.create_divestment_value_change_on_moneybird(disposal_date)
                messages.success(
                    request,
                    f'Asset "{asset.name}" has been successfully divested on Moneybird.',
                )
            else:
                # For out_of_use, use fully depreciate which automatically creates an "out-of-use" disposal
                description = f"Full depreciation - out of use"
                asset.fully_depreciate_on_moneybird(disposal_date, description)
                messages.success(
                    request,
                    f'Asset "{asset.name}" has been successfully disposed on Moneybird as out of use.',
                )
        except Exception as e:
            messages.error(
                request,
                f'Failed to dispose asset "{asset.name}" on Moneybird: {str(e)}',
            )

        return redirect(
            request.META.get(
                "HTTP_REFERER", reverse("inventory_frontend:detail", kwargs={"pk": pk})
            )
        )


class BulkStatusChangeView(LoginRequiredMixin, TemplateView):
    template_name = "bulk_update.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["form"] = BulkStatusChangeForm()
        context["asset_states"] = AssetStates.choices
        return context

    def post(self, request, *args, **kwargs):
        form = BulkStatusChangeForm(request.POST)

        if form.is_valid():
            # Parse asset IDs from hidden input
            asset_ids_json = request.POST.get("asset_ids", "[]")
            try:
                asset_ids = json.loads(asset_ids_json)
            except json.JSONDecodeError:
                messages.error(request, "Invalid asset data")
                return self.render_to_response(self.get_context_data(form=form))

            if not asset_ids:
                messages.error(request, "Please select at least one asset")
                return self.render_to_response(self.get_context_data(form=form))

            # Get form data
            status_date = form.cleaned_data["status_date"]
            new_status = form.cleaned_data.get("new_status")
            comments = form.cleaned_data.get("comments", "")
            contact_id = form.cleaned_data.get("contact_id")

            # Handle empty new_status
            if new_status == "":
                new_status = None

            # Get contact if provided
            contact = None
            if contact_id:
                try:
                    contact = Contact.objects.get(id=contact_id)
                except Contact.DoesNotExist:
                    pass

            # Create status changes for all selected assets
            created_count = 0
            failed_assets = []

            for asset_id in asset_ids:
                try:
                    asset = Asset.objects.get(id=asset_id)
                    StatusChange.objects.create(
                        asset=asset,
                        status_date=status_date,
                        new_status=new_status,
                        comments=comments,
                        contact=contact,
                    )
                    created_count += 1
                except Asset.DoesNotExist:
                    failed_assets.append(asset_id)
                except Exception as e:
                    failed_assets.append(f"{asset_id} ({str(e)})")

            # Show success/error messages
            if created_count > 0:
                messages.success(
                    request,
                    f"Successfully created {created_count} status change(s)",
                )

            if failed_assets:
                messages.warning(
                    request,
                    f"Failed to create status changes for some assets: {', '.join(map(str, failed_assets))}",
                )

            return redirect("inventory_frontend:bulk_update")

        return self.render_to_response(self.get_context_data(form=form))

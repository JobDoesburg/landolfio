from django.contrib import messages
from django.shortcuts import redirect
from django.urls import reverse
from django.views.generic import ListView, DetailView, CreateView
from django.db.models import Q
from django.http import JsonResponse
from django_drf_filepond.api import store_upload
from django_drf_filepond.models import TemporaryUpload
from django.views import View

from inventory.models.asset import Asset, AssetStates
from inventory.models.asset_on_document_line import AssetOnJournalDocumentLine
from inventory.models.asset_property import AssetProperty, AssetPropertyValue
from inventory.models.attachment import Attachment, attachments_directory_path
from inventory.models.category import Category
from inventory.models.collection import Collection
from inventory.models.location import Location
from inventory.models.remarks import Remark
from accounting.models import JournalDocumentLine
from inventory_frontend.forms import AssetForm

from django.db.models import Count, Prefetch
from django.views.generic import TemplateView
from django.views.generic.edit import DeleteView
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.views.generic.edit import UpdateView
from django.contrib.messages.views import SuccessMessageMixin


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

        # Get categories with counts
        context["categories"] = Category.objects.annotate(
            asset_count=Count("asset")
        ).order_by("-asset_count")[:5]

        # Get locations with counts
        context["locations"] = Location.objects.annotate(
            asset_count=Count("asset")
        ).order_by("-asset_count")[:5]

        # Get collections with counts
        context["collections"] = Collection.objects.annotate(
            asset_count=Count("asset")
        ).order_by("-asset_count")[:5]

        return context


class AssetListView(LoginRequiredMixin, ListView):
    template_name = "list.html"
    context_object_name = "assets"
    model = Asset
    paginate_by = 12

    def get_queryset(self):
        queryset = super().get_queryset()

        # Get filter parameters (support multiple values)
        search_query = self.request.GET.get("q")
        categories = self.request.GET.getlist("category")
        statuses = self.request.GET.getlist("status")
        locations = self.request.GET.getlist("location")
        collections = self.request.GET.getlist("collection")
        min_value = self.request.GET.get("min_value")
        max_value = self.request.GET.get("max_value")

        # Apply filters
        if search_query and search_query.strip():
            queryset = queryset.filter(
                Q(name__icontains=search_query.strip())
                | Q(category__name__icontains=search_query.strip())
            )

        if categories:
            # Filter non-empty values
            categories = [cat for cat in categories if cat.strip()]
            if categories:
                queryset = queryset.filter(category_id__in=categories)

        if statuses:
            # Filter non-empty values
            statuses = [stat for stat in statuses if stat.strip()]
            if statuses:
                queryset = queryset.filter(local_status__in=statuses)

        if locations:
            # Filter non-empty values
            locations = [loc for loc in locations if loc.strip()]
            if locations:
                queryset = queryset.filter(location_id__in=locations)

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

        # Apply property filters
        property_filters = self._get_property_filters()
        for property_filter in property_filters:
            queryset = queryset.filter(property_filter)

        return queryset.select_related("category", "location", "collection", "size")

    def _parse_property_parameters(self):
        """Parse property-related parameters from the request."""
        property_params = {}
        
        for param_name, param_values in self.request.GET.lists():
            try:
                if param_name.endswith(('_min', '_max')):
                    self._handle_numeric_property_param(param_name, param_values, property_params)
                else:
                    self._handle_property_param(param_name, param_values, property_params)
            except (ValueError, TypeError, AssetProperty.DoesNotExist):
                continue
        
        return property_params
    
    def _handle_numeric_property_param(self, param_name, param_values, property_params):
        """Handle numeric property range parameters (min/max)."""
        property_slug = param_name.replace('_min', '').replace('_max', '')
        range_type = 'min' if param_name.endswith('_min') else 'max'
        
        property_obj = AssetProperty.objects.get(slug=property_slug)
        property_id = property_obj.id
        
        if property_id not in property_params:
            property_params[property_id] = {'type': 'number', 'obj': property_obj}
        
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
                'type': property_obj.property_type,
                'values': non_empty_values,
                'obj': property_obj
            }
    
    def _build_property_filters(self, property_params):
        """Build Django Q objects for property filtering."""
        filters = []
        
        for property_id, params in property_params.items():
            property_type = params['type']
            
            if property_type == 'number':
                filter_q = self._build_numeric_filter(property_id, params)
            elif property_type == 'dropdown':
                filter_q = self._build_dropdown_filter(property_id, params)
            else:  # string
                filter_q = self._build_string_filter(property_id, params)
            
            if filter_q:
                filters.append(filter_q)
        
        return filters
    
    def _build_numeric_filter(self, property_id, params):
        """Build filter for numeric properties."""
        has_min = 'min' in params
        has_max = 'max' in params
        
        if has_min or has_max:
            return (
                Q(property_values__property_id=property_id) &
                Q(property_values__value__regex=r'^[0-9]+\.?[0-9]*$') &
                ~Q(property_values__value='')
            )
        return None
    
    def _build_dropdown_filter(self, property_id, params):
        """Build filter for dropdown properties."""
        values = params.get('values', [])
        if not values:
            return None
        
        value_filters = Q()
        for value in values:
            value_filters |= Q(property_values__value__exact=value)
        
        return Q(property_values__property_id=property_id) & value_filters
    
    def _build_string_filter(self, property_id, params):
        """Build filter for string properties."""
        values = params.get('values', [])
        if not values:
            return None
        
        return (
            Q(property_values__property_id=property_id) &
            Q(property_values__value__icontains=values[0])
        )
    
    def _get_property_filters(self):
        """Extract and build property filter conditions from request parameters."""
        property_params = self._parse_property_parameters()
        return self._build_property_filters(property_params)
    
    def _get_properties_with_current_values(self):
        """Get all properties with their current filter values attached."""
        properties = AssetProperty.objects.select_related("category").order_by("category__name", "order", "name")
        
        for prop in properties:
            prop.current_values = self.request.GET.getlist(prop.slug)
            
            # For numeric properties, also add min/max values
            if prop.property_type == 'number':
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
                    self._add_display_filter(property_filters, param_name, param_value, property_obj)
            except AssetProperty.DoesNotExist:
                continue
        
        return property_filters
    
    def _get_property_from_param(self, param_name):
        """Extract property object from parameter name."""
        if param_name.endswith(('_min', '_max')):
            property_slug = param_name.replace('_min', '').replace('_max', '')
            return AssetProperty.objects.get(slug=property_slug)
        else:
            return AssetProperty.objects.get(slug=param_name)
    
    def _add_display_filter(self, property_filters, param_name, param_value, property_obj):
        """Add filter to display filters dictionary."""
        property_id = property_obj.id
        
        if param_name.endswith(('_min', '_max')):
            range_type = 'min' if param_name.endswith('_min') else 'max'
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
                if key.endswith(('_min', '_max')):
                    property_slug = key.replace('_min', '').replace('_max', '')
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

        # Get locations grouped by location group with counts
        from inventory.models.location import LocationGroup
        from django.db.models import Prefetch

        # Prefetch locations with their asset counts
        locations_with_counts = Location.objects.annotate(
            asset_count=Count("asset")
        ).order_by("order", "pk")

        location_groups = (
            LocationGroup.objects.prefetch_related(
                Prefetch("location_set", queryset=locations_with_counts)
            )
            .annotate(asset_count=Count("location__asset"))
            .order_by("order", "pk")
        )

        context["location_groups"] = location_groups

        # Get collections with counts
        context["collections"] = Collection.objects.annotate(
            asset_count=Count("asset")
        ).order_by("name")

        # Add asset states in logical color grouping order
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

        # Get all properties for the filter dropdown with current values
        context["all_properties"] = self._get_properties_with_current_values()

        # Parse property filters for display
        property_filters = self._parse_property_filters_for_display()
        property_filter_count = self._count_active_property_filters()

        # Add current filter values
        context["current_filters"] = {
            "q": self.request.GET.get("q", ""),
            "categories": self.request.GET.getlist("category"),
            "statuses": self.request.GET.getlist("status"),
            "locations": self.request.GET.getlist("location"),
            "collections": self.request.GET.getlist("collection"),
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

        # Add financial data
        context["financial_data"] = {
            "purchase_value": asset.purchase_value,
            "sales_profit": asset.sales_profit,
            "total_profit": asset.total_profit,
            "total_revenue": asset.total_revenue_value,
            "total_expenses": asset.total_expenses_value,
            "total_direct_costs": asset.total_direct_costs_value,
        }

        # Add status information
        context["accounting_status"] = asset.accounting_status
        context["accounting_errors"] = asset.accounting_errors
        context["is_rented"] = asset.is_rented
        context["has_rental_agreement"] = asset.has_rental_agreement
        context["has_loan_agreement"] = asset.has_loan_agreement

        # Add related documents
        context["rental_agreements"] = asset.estimate_document_lines.filter(
            document__workflow__is_rental=True,
            document__state__in=["open", "late", "accepted"],
        )

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
        context["locations"] = Location.objects.all().order_by("order", "name")

        context["journal_history"] = (
            AssetOnJournalDocumentLine.objects.filter(asset=asset)
            .select_related("document_line__ledger_account")
            .prefetch_related(
                Prefetch(
                    "document_line",
                    queryset=JournalDocumentLine.objects.select_subclasses()
                )
            )
        )

        # Add asset properties
        category_properties = AssetProperty.objects.filter(
            category=asset.category
        ).order_by("order", "name")
        
        # Get existing property values for this asset
        existing_values = {
            pv.property_id: pv 
            for pv in AssetPropertyValue.objects.filter(asset=asset)
            .select_related("property")
        }
        
        # Create a list of properties with their current values
        properties_with_values = []
        for prop in category_properties:
            value_obj = existing_values.get(prop.id)
            properties_with_values.append({
                'property': prop,
                'value_obj': value_obj,
                'current_value': value_obj.value if value_obj else '',
                'formatted_value': value_obj.get_formatted_value() if value_obj else '',
            })
        
        context["asset_properties"] = properties_with_values

        # Build back URL to list view with preserved parameters
        back_url = reverse('inventory_frontend:list')
        referer = self.request.META.get('HTTP_REFERER', '')
        
        # If coming from list view, preserve the query parameters
        if '/list/' in referer and '?' in referer:
            query_params = referer.split('?', 1)[1]
            back_url += '?' + query_params
        
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

        # Handle status update
        if data.get("action") == "update_status":
            updated_fields = []

            # Update local status
            new_local_status = data.get("new_local_status", "").strip()
            if new_local_status and new_local_status != asset.local_status:
                asset.local_status = new_local_status
                updated_fields.append("status")

            # Update location
            new_location_id = data.get("new_location", "").strip()
            if new_location_id:
                try:
                    new_location = Location.objects.get(pk=new_location_id)
                    if new_location != asset.location:
                        asset.location = new_location
                        updated_fields.append("location")
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
                        updated_fields.append("location number")
                except ValueError:
                    messages.error(request, "Invalid location number")
                    return redirect(request.path)
            elif new_location_nr == "" and asset.location_nr is not None:
                # Clear location number if empty string provided
                asset.location_nr = None
                updated_fields.append("location number (cleared)")

            if updated_fields:
                asset.save()
                messages.success(
                    request, f"Updated {', '.join(updated_fields)} successfully"
                )
            else:
                messages.info(request, "No changes made")

            return redirect(request.path)

        # Handle property updates
        if data.get("action") == "update_properties":
            updated_properties = self._update_asset_properties(asset, data)
            
            if updated_properties:
                messages.success(
                    request, 
                    f"Updated properties: {', '.join(updated_properties)}"
                )
            else:
                messages.info(request, "No property changes made")
            
            return redirect(request.path)
    
    def _update_asset_properties(self, asset, data):
        """Update asset property values from form data."""
        updated_properties = []
        category_properties = AssetProperty.objects.filter(category=asset.category)
        
        for prop in category_properties:
            field_name = f"property_{prop.slug}"
            new_value = data.get(field_name, "").strip()
            
            if new_value:
                updated_properties.extend(self._set_property_value(asset, prop, new_value))
            else:
                updated_properties.extend(self._clear_property_value(asset, prop))
        
        return updated_properties
    
    def _set_property_value(self, asset, prop, new_value):
        """Set or update a property value for an asset."""
        property_value, created = AssetPropertyValue.objects.get_or_create(
            asset=asset,
            property=prop,
            defaults={'value': new_value}
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

            attachment = Attachment(asset=asset)
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


class AssetCreateView(LoginRequiredMixin, CreateView):
    template_name = "create.html"
    model = Asset
    form_class = AssetForm
    success_url = reverse_lazy("inventory_frontend:list")

    def form_valid(self, form):
        # Set default status for new assets
        form.instance.local_status = AssetStates.PLACEHOLDER
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["categories"] = Category.objects.all()
        context["locations"] = Location.objects.all()
        context["collections"] = Collection.objects.all()
        return context


class AssetUpdateView(LoginRequiredMixin, SuccessMessageMixin, UpdateView):
    model = Asset
    form_class = AssetForm
    template_name = "update.html"
    success_message = "Asset was updated successfully"

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
                    "category": asset.category.name_singular
                    if asset.category
                    else None,
                    "size": str(asset.size) if asset.size else None,
                    "location": str(asset.location) if asset.location else None,
                    "location_nr": asset.location_nr,
                    "created_at": asset.created_at.strftime("%d-%m-%Y")
                    if asset.created_at
                    else None,
                    "purchase_value": float(asset.purchase_value)
                    if asset.purchase_value
                    else 0,
                    "listing_price": float(asset.listing_price)
                    if asset.listing_price
                    else 0,
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

        # Get distinct values for this property from assets in the same category that match the query
        values = (
            AssetPropertyValue.objects.filter(
                property=property_obj,
                asset__category=property_obj.category,  # Only from same category
                value__icontains=query
            )
            .values_list("value", flat=True)
            .distinct()
            .order_by("value")[:10]
        )

        suggestions = [{"value": value} for value in values if value]

        return JsonResponse(suggestions, safe=False)

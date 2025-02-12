from django.contrib import messages
from django.shortcuts import redirect
from django.views.generic import ListView, DetailView, CreateView, UpdateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q
from django.http import JsonResponse
from django.urls import reverse_lazy
from django_drf_filepond.api import store_upload
from django_drf_filepond.models import TemporaryUpload

from inventory.models.asset import Asset, AssetStates
from inventory.models.attachment import Attachment, attachments_directory_path
from inventory.models.category import Category
from inventory.models.collection import Collection
from inventory.models.location import Location
from inventory_frontend.forms import AssetForm

from django.db.models import Count
from django.views.generic import TemplateView
from django.views.generic.edit import DeleteView
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.views.generic.edit import UpdateView
from django.contrib.messages.views import SuccessMessageMixin


class AssetSearchView(TemplateView):
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

        # Get filter parameters
        search_query = self.request.GET.get("q")
        category = self.request.GET.get("category")
        status = self.request.GET.get("status")
        location = self.request.GET.get("location")
        collection = self.request.GET.get("collection")
        min_value = self.request.GET.get("min_value")
        max_value = self.request.GET.get("max_value")

        # Apply filters
        if search_query:
            queryset = queryset.filter(
                Q(name__icontains=search_query)
                | Q(category__name__icontains=search_query)
            )

        if category:
            queryset = queryset.filter(category_id=category)

        if status:
            queryset = queryset.filter(local_status=status)

        if location:
            queryset = queryset.filter(location_id=location)

        if collection:
            queryset = queryset.filter(collection_id=collection)

        if min_value:
            queryset = queryset.filter(listing_price__gte=min_value)

        if max_value:
            queryset = queryset.filter(listing_price__lte=max_value)

        return queryset.select_related("category", "location", "collection", "size")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Get base queryset for filtered counts
        base_qs = self.get_queryset()

        # Get categories with counts
        context["categories"] = Category.objects.annotate(
            asset_count=Count("asset")
        ).order_by("name")

        # Get locations with counts
        context["locations"] = Location.objects.annotate(
            asset_count=Count("asset")
        ).order_by("name")

        # Get collections with counts
        context["collections"] = Collection.objects.annotate(
            asset_count=Count("asset")
        ).order_by("name")

        # Add asset states
        context["asset_states"] = AssetStates.choices

        # Add current filter values
        context["current_filters"] = {
            "q": self.request.GET.get("q", ""),
            "category": self.request.GET.get("category", ""),
            "status": self.request.GET.get("status", ""),
            "location": self.request.GET.get("location", ""),
            "collection": self.request.GET.get("collection", ""),
            "min_value": self.request.GET.get("min_value", ""),
            "max_value": self.request.GET.get("max_value", ""),
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
            .prefetch_related(
                "journal_document_lines",
                "estimate_document_lines",
                "recurring_sales_invoice_document_lines",
            )
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

        return context

    def post(self, request, *args, **kwargs):
        asset = self.get_object()
        data = request.POST

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

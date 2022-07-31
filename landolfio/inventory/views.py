import json
import os

from django.contrib.admin.views.decorators import staff_member_required
from django.core.files.base import ContentFile
from django.http import HttpResponseBadRequest, HttpResponse
from django.shortcuts import redirect
from django.utils.decorators import method_decorator
from django.views.generic import TemplateView, DetailView
from django_drf_filepond.api import store_upload
from django_drf_filepond.models import TemporaryUpload, StoredUpload

from inventory.models.asset import Asset
from inventory.models.attachment import Attachment, attachments_directory_path
from inventory.models.category import AssetCategory


@method_decorator(staff_member_required, name="dispatch")
class ViewAssetView(DetailView):

    template_name = "admin/view_asset.html"
    model = Asset
    context_object_name = "asset"
    pk_url_kwarg = "id"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["is_popup"] = False
        context["is_nav_sidebar_enabled"] = True
        context["assets"] = Asset.objects.filter(category=self.object.category).all()
        context["asset_sizes"] = (
            Asset.objects.filter(category=self.object.category)
            .values_list("size__name", flat=True)
            .distinct()
            .order_by()
        )
        context["categories"] = AssetCategory.objects.all()
        return context

    def post(self, request, *args, **kwargs):
        data = request.POST
        try:
            filepond_ids = data.getlist("filepond")
        except KeyError:
            return HttpResponseBadRequest("Missing filepond key in form.")

        if not isinstance(filepond_ids, list):
            return HttpResponseBadRequest("Unexpected data type in form.")

        stored_uploads = []
        for upload_id in filepond_ids:
            if upload_id == "":
                continue

            tu = TemporaryUpload.objects.get(upload_id=upload_id)
            asset = self.get_object()
            attachment = Attachment(asset=asset)
            stored_upload = store_upload(
                upload_id, attachments_directory_path(attachment, tu.upload_name)
            )
            attachment.attachment = stored_upload.file
            attachment.save()
            stored_uploads.append(upload_id)

        # Return the list of uploads that were stored.
        return redirect(self.request.path)


@method_decorator(staff_member_required, name="dispatch")
class AssetCategoryView(DetailView):
    template_name = "admin/view_asset_category.html"
    model = AssetCategory
    context_object_name = "asset_category"
    pk_url_kwarg = "id"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["is_popup"] = False
        context["is_nav_sidebar_enabled"] = True
        context["assets"] = Asset.objects.filter(category=self.object).all()
        context["asset_sizes"] = (
            Asset.objects.filter(category=self.object)
            .values_list("size__name", flat=True)
            .distinct()
            .order_by()
        )
        context["categories"] = AssetCategory.objects.all()
        context["asset"] = None
        return context

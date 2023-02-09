from django.contrib.admin.views.decorators import staff_member_required
from django.shortcuts import redirect
from django.utils.decorators import method_decorator
from django.views.generic import DetailView, TemplateView
from django_drf_filepond.api import store_upload
from django_drf_filepond.models import TemporaryUpload

from inventory.models.asset import Asset
from inventory.models.remarks import Remark
from inventory.models.attachment import Attachment, attachments_directory_path


@method_decorator(staff_member_required, name="dispatch")
class ViewAssetView(DetailView):
    template_name = "admin/inventory/view_asset/view_asset.html"
    model = Asset
    context_object_name = "asset"
    pk_url_kwarg = "id"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["is_popup"] = False
        context["is_nav_sidebar_enabled"] = True
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

            tu = TemporaryUpload.objects.get(upload_id=upload_id)
            attachment = Attachment(asset=asset)
            stored_upload = store_upload(
                upload_id, attachments_directory_path(attachment, tu.upload_name)
            )
            attachment.attachment = stored_upload.file
            attachment.save()
            stored_uploads.append(upload_id)

        try:
            remark = data.get("remark")
            if remark and remark != "":
                Remark.objects.create(asset=asset, remark=remark)
        except KeyError:
            pass
        return redirect(self.request.path)


class AssetOverviewView(TemplateView):
    template_name = "admin/inventory/overview/index.html"

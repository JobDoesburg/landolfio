from django.contrib import messages
from django.contrib.admin.models import LogEntry
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.contenttypes.models import ContentType
from django.forms import ModelForm
from django.shortcuts import redirect
from django.utils.decorators import method_decorator
from django.views.generic import DetailView, TemplateView
from django_drf_filepond.api import store_upload
from django_drf_filepond.models import TemporaryUpload

from inventory.models.asset import Asset
from inventory.models.remarks import Remark
from inventory.models.attachment import Attachment, attachments_directory_path


class NewStatusForm(ModelForm):
    class Meta:
        model = Asset
        fields = ["local_status", "location", "location_nr"]


@method_decorator(staff_member_required, name="dispatch")
class ViewAssetView(DetailView):
    template_name = "admin/inventory/asset/view_asset/view_asset.html"
    model = Asset
    context_object_name = "asset"
    pk_url_kwarg = "id"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["is_popup"] = False
        context["is_nav_sidebar_enabled"] = True
        context["status_form"] = NewStatusForm(instance=self.get_object())
        return context

    def process_filepond(self, request):
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
                self.message_user(
                    request,
                    f"Upload with id {upload_id} does not exist",
                    level=messages.ERROR,
                )
                continue

            attachment = Attachment(asset=asset)
            stored_upload = store_upload(
                upload_id, attachments_directory_path(attachment, tu.upload_name)
            )
            attachment.attachment = stored_upload.file
            attachment.save()
            stored_uploads.append(upload_id)

    def process_remarks(self, request):
        asset = self.get_object()
        data = request.POST

        try:
            remark = data.get("remark")
            if remark and remark != "":
                Remark.objects.create(asset=asset, remark=remark)
        except KeyError:
            pass

    def process_status(self, request):
        asset = self.get_object()
        form = NewStatusForm(request.POST, instance=asset)
        if form.is_valid():
            form.save()
            LogEntry.objects.log_action(
                user_id=request.user.id,
                content_type_id=ContentType.objects.get_for_model(asset).pk,
                object_id=asset.id,
                object_repr=str(asset),
                action_flag=2,
                change_message=f"Status changed to {asset.local_status}, {asset.location}",
            )

    def post(self, request, *args, **kwargs):
        self.process_filepond(request)
        self.process_remarks(request)
        self.process_status(request)
        return redirect(self.request.path)


class AssetOverviewView(TemplateView):
    template_name = "admin/inventory/asset/overview/index.html"

from django.contrib import messages
from django.contrib.admin.views.decorators import staff_member_required
from django.core.exceptions import ValidationError
from django.shortcuts import redirect
from django.urls import reverse
from django.utils.translation import gettext_lazy as _

from scantags.models import ScanTag


@staff_member_required
def tag_scan_view(request, *args, **kwargs):
    tag_id = kwargs.get("id")
    try:
        scan_tag = ScanTag.objects.get(id=tag_id)
        if scan_tag.asset:
            return redirect(
                reverse("assets_admin:view_asset", args=[scan_tag.asset_id])
            )
        else:
            messages.warning(
                request, _("Tag {} is not linked to an asset.").format(tag_id)
            )
            return redirect(
                reverse("admin:scantags_scantag_change", args=[scan_tag.id])
            )
    except ScanTag.DoesNotExist:
        scan_tag = ScanTag(id=tag_id)
        try:
            scan_tag.full_clean()
            scan_tag.save()
        except ValidationError as e:
            messages.error(
                request, _("Scanned a tag with an invalid id: {}").format(e.messages)
            )
            return redirect(reverse("admin:scantags_scantag_changelist"))
        else:
            messages.success(request, _("New tag generated: {}").format(tag_id))
            return redirect(
                reverse("admin:scantags_scantag_change", args=[scan_tag.id])
            )

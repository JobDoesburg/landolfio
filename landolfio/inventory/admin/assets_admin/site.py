from django.contrib import admin
from django.utils.translation import gettext_lazy as _

from inventory.admin.assets_admin.utils import get_extra_assets_context


class AssetAdminSite(admin.AdminSite):
    site_header = _("Landolfio") + " " + _("assets")
    site_title = _("Landolfio") + " " + _("assets")
    index_template = "assets_admin/index.html"
    app_index_template = "assets_admin/app_index.html"

    def index(self, request, extra_context=None):
        extra_context = extra_context or {}
        extra_context = get_extra_assets_context(extra_context)
        return super().index(request, extra_context=extra_context)

    def app_index(self, request, app_label, extra_context=None):
        extra_context = extra_context or {}
        extra_context = get_extra_assets_context(extra_context)
        return super().app_index(request, app_label, extra_context=extra_context)


assets_admin = AssetAdminSite(name="assets_admin")

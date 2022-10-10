from django.conf import settings
from django.conf.urls.i18n import i18n_patterns
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include
from django.urls import path
from django.urls import re_path
from django.views.generic.base import RedirectView

from . import views
from inventory.admin.assets_admin import assets_admin

urlpatterns = [
    path("admin/", admin.site.urls),
    path("assets/", assets_admin.urls),
    path("moneybird/", include("moneybird.webhooks.urls")),
    path("api/accounting/", include("accounting.api.urls")),
    path("fp/", include("django_drf_filepond.urls")),
    path("scan/", include("scantags.urls")),
    re_path(r"^media/", views.protected_ask_reverse_proxy),
    path("", RedirectView.as_view(url="/assets/"), name="index"),
    path("admin/", RedirectView.as_view(url="/admin/"), name="admin"),
]
urlpatterns += (path("customer/", include("rental_customers.urls")),)

if settings.DEBUG:
    import debug_toolbar

    urlpatterns += [path("__debug__/", include(debug_toolbar.urls))]

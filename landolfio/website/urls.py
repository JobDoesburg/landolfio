from django.conf import settings
from django.contrib import admin
from django.urls import include
from django.urls import path
from django.urls import re_path
from django.views.generic.base import RedirectView

from . import views

urlpatterns = [
    path("admin/", admin.site.urls),
    path("moneybird/", include("moneybird.webhooks.urls")),
    path("api/accounting/", include("accounting.api.urls")),
    path("fp/", include("django_drf_filepond.urls")),
    path("scan/", include("scantags.urls")),
    re_path(r"^media/", views.protected_ask_reverse_proxy),
    path("admin/", RedirectView.as_view(url="/admin/"), name="admin"),
    path(
        "", RedirectView.as_view(url="/admin/inventory/asset/overview/"), name="admin"
    ),
]
urlpatterns += (path("customer/", include("new_customers.urls")),)
urlpatterns += (path("customer/rental/", include("new_rental_customers.urls")),)

if settings.DEBUG:
    import debug_toolbar

    urlpatterns += [path("__debug__/", include(debug_toolbar.urls))]
    urlpatterns += [
        path("media/", views.protected_ask_reverse_proxy),
    ]

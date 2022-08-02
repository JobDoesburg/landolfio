from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include
from django.urls import path
from django.urls import re_path
from django.views.generic.base import RedirectView

from . import views

urlpatterns = (
    static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    + [
        path("admin/", admin.site.urls),
        path("moneybird/", include("moneybird.webhooks.urls")),
        path("api/accounting/", include("accounting.api.urls")),
        path("fp/", include("django_drf_filepond.urls")),
        re_path(r"^media/", views.protected_ask_reverse_proxy),
        # Always redirect to the admin interface as a fallback
        re_path(r"^.*", RedirectView.as_view(url="/admin/")),
    ]
)

"""website URL Configuration.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include
from django.urls import path
from django.urls import re_path
from django.views.generic.base import RedirectView

# Static files are NOT authenticated and should be replaced by files in an S3 bucket.
urlpatterns = static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT) + [
    re_path("api/accounting/", include("accounting.api.urls")),
    path("admin/", admin.site.urls),
    # The admin interface is the only thing we serve, so just always redirect
    # there if we get an unknown path
    re_path(r"^.*", RedirectView.as_view(url="/admin/")),
]

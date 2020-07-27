from django.conf import settings
from django.conf.urls import url
from django.contrib import admin
from django.contrib.auth.decorators import login_required
from django.urls import path
from django.views.static import serve


@login_required(redirect_field_name="next", login_url="admin:login")
def protected_serve(request, path, document_root=None, show_indexes=True):
    if request.user.is_authenticated and request.user.has_perm("media.view_mediaitem"):
        return serve(request, path, document_root, show_indexes)


urlpatterns = [
    path("", admin.site.urls, name="admin"),
    url(r"^%s(?P<path>.*)$" % settings.MEDIA_URL[1:], protected_serve, {"document_root": settings.MEDIA_ROOT}),
]

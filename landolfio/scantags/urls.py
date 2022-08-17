from django.urls import path

from scantags import views

urlpatterns = [
    path("<str:id>/", views.tag_scan_view, name="scan"),
]

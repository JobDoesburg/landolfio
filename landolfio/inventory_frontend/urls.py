from django.urls import path
from .views import (
    AssetSearchView,
    AssetListView,
    AssetDetailView,
    AssetCreateView,
    AssetDeleteView,
    AssetUpdateView,
)

app_name = "inventory_frontend"

urlpatterns = [
    path("", AssetSearchView.as_view(), name="search"),
    path("list/", AssetListView.as_view(), name="list"),
    path("<uuid:pk>/", AssetDetailView.as_view(), name="detail"),
    path("create/", AssetCreateView.as_view(), name="create"),
    path("asset/<uuid:pk>/update/", AssetUpdateView.as_view(), name="update"),
    path("asset/<uuid:pk>/delete/", AssetDeleteView.as_view(), name="delete"),
]

from django.urls import path
from .views import (
    PublicIndexView,
    AssetSearchView,
    AssetListView,
    AssetDetailView,
    AssetCreateView,
    AssetDeleteView,
    AssetUpdateView,
    AssetAutocompleteView,
)

app_name = "inventory_frontend"

urlpatterns = [
    path("", PublicIndexView.as_view(), name="public_index"),
    path("search/", AssetSearchView.as_view(), name="search"),
    path("list/", AssetListView.as_view(), name="list"),
    path("autocomplete/", AssetAutocompleteView.as_view(), name="autocomplete"),
    path("<uuid:pk>/", AssetDetailView.as_view(), name="detail"),
    path("create/", AssetCreateView.as_view(), name="create"),
    path("asset/<uuid:pk>/update/", AssetUpdateView.as_view(), name="update"),
    path("asset/<uuid:pk>/delete/", AssetDeleteView.as_view(), name="delete"),
]

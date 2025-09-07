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
    PropertyValueAutocompleteView,
    AttachmentDeleteView,
    AttachmentReorderView,
    AssetCreateMoneybirdView,
    AssetLinkMoneybirdView,
    AssetUnlinkMoneybirdView,
    AssetDeleteMoneybirdView,
    AssetRefreshMoneybirdView,
    AssetUpdateMoneybirdView,
    AssetDisposeMoneybirdView,
)

app_name = "inventory_frontend"

urlpatterns = [
    path("", PublicIndexView.as_view(), name="public_index"),
    path("search/", AssetSearchView.as_view(), name="search"),
    path("list/", AssetListView.as_view(), name="list"),
    path("autocomplete/", AssetAutocompleteView.as_view(), name="autocomplete"),
    path(
        "property-autocomplete/",
        PropertyValueAutocompleteView.as_view(),
        name="property_autocomplete",
    ),
    path("<uuid:pk>/", AssetDetailView.as_view(), name="detail"),
    path("create/", AssetCreateView.as_view(), name="create"),
    path("asset/<uuid:pk>/update/", AssetUpdateView.as_view(), name="update"),
    path("asset/<uuid:pk>/delete/", AssetDeleteView.as_view(), name="delete"),
    path(
        "<uuid:asset_pk>/attachment/<int:attachment_pk>/delete/",
        AttachmentDeleteView.as_view(),
        name="attachment_delete",
    ),
    path(
        "<uuid:asset_pk>/attachments/reorder/",
        AttachmentReorderView.as_view(),
        name="attachment_reorder",
    ),
    path(
        "asset/<uuid:pk>/create-moneybird/",
        AssetCreateMoneybirdView.as_view(),
        name="create_moneybird",
    ),
    path(
        "asset/<uuid:pk>/link-moneybird/",
        AssetLinkMoneybirdView.as_view(),
        name="link_moneybird",
    ),
    path(
        "asset/<uuid:pk>/unlink-moneybird/",
        AssetUnlinkMoneybirdView.as_view(),
        name="unlink_moneybird",
    ),
    path(
        "asset/<uuid:pk>/delete-moneybird/",
        AssetDeleteMoneybirdView.as_view(),
        name="delete_moneybird",
    ),
    path(
        "asset/<uuid:pk>/refresh-moneybird/",
        AssetRefreshMoneybirdView.as_view(),
        name="refresh_moneybird",
    ),
    path(
        "asset/<uuid:pk>/update-moneybird/",
        AssetUpdateMoneybirdView.as_view(),
        name="update_moneybird",
    ),
    path(
        "asset/<uuid:pk>/dispose-moneybird/",
        AssetDisposeMoneybirdView.as_view(),
        name="dispose_moneybird",
    ),
]

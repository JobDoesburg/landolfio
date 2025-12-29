from django.urls import path

from .views import (
    AssetAutocompleteView,
    AssetCreateMoneybirdView,
    AssetCreateView,
    AssetDeleteMoneybirdView,
    AssetDeleteView,
    AssetDetailView,
    AssetDisposeMoneybirdView,
    AssetLinkMoneybirdView,
    AssetListView,
    AssetRefreshMoneybirdView,
    AssetSearchView,
    AssetUnlinkMoneybirdView,
    AssetUpdateMoneybirdView,
    AssetUpdateView,
    AttachmentDeleteView,
    AttachmentDownloadZipView,
    AttachmentReorderView,
    BulkStatusChangeView,
    ContactAutocompleteView,
    PropertyValueAutocompleteView,
    PublicIndexView,
)

app_name = "inventory_frontend"

urlpatterns = [
    path("", PublicIndexView.as_view(), name="public_index"),
    path("search/", AssetSearchView.as_view(), name="search"),
    path("list/", AssetListView.as_view(), name="list"),
    path("bulk-update/", BulkStatusChangeView.as_view(), name="bulk_update"),
    path("autocomplete/", AssetAutocompleteView.as_view(), name="autocomplete"),
    path(
        "property-autocomplete/",
        PropertyValueAutocompleteView.as_view(),
        name="property_autocomplete",
    ),
    path(
        "contact-autocomplete/",
        ContactAutocompleteView.as_view(),
        name="contact_autocomplete",
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
        "<uuid:asset_pk>/attachments/download-zip/",
        AttachmentDownloadZipView.as_view(),
        name="attachment_download_zip",
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

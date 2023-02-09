from django.contrib import admin
from django.utils.safestring import mark_safe
from django.utils.translation import gettext_lazy as _
from queryable_properties.admin import (
    QueryablePropertiesAdminMixin,
)
from accounting.models.ledger_account import LedgerAccountType
from inventory.models.asset import (
    AssetOnJournalDocumentLine,
    AssetOnEstimateDocumentLine,
    AssetOnRecurringSalesInvoiceDocumentLine,
)
from inventory.models.attachment import Attachment
from inventory.models.remarks import Remark


def is_an_image_path(path: str) -> bool:
    """Return true if the path points to an image."""
    extension = path.split(".")[-1]
    return extension in ("jpg", "jpeg", "png")


class AttachmentInlineAdmin(admin.StackedInline):
    """Attachment inline admin."""

    def show_image(self, obj):
        # pylint: disable=no-self-use
        """Show a file as an image if it is one."""
        if is_an_image_path(obj.attachment.name):
            return mark_safe(f'<img src="{obj.attachment.url}" height="600px"/>')
        return _("Not an image")

    show_image.short_description = _("Image")

    model = Attachment
    readonly_fields = ["show_image", "upload_date"]
    extra = 0


class RemarkInline(admin.StackedInline):
    model = Remark
    fields = ["date", "remark"]
    readonly_fields = ["date"]
    extra = 1

    def has_change_permission(self, request, obj=None):
        return False


class DocumentLineInline(QueryablePropertiesAdminMixin, admin.TabularInline):
    extra = 0
    can_delete = False

    @admin.display(description=_("Workflow"))
    def workflow(self, obj):
        return obj.document_line.document.workflow

    @admin.display(description=_("View on Moneybird"))
    def view_on_moneybird(self, obj):
        url = obj.document_line.document.moneybird_url

        if url is None:
            return None
        return mark_safe(
            f'<a class="button small" href="{url}" target="_blank" style="white-space: nowrap;">{_("View on Moneybird")}</a>'
        )

    def has_add_permission(self, request, obj):
        return False


class JournalDocumentLineInline(DocumentLineInline):
    model = AssetOnJournalDocumentLine

    fields = [
        "date",
        "description",
        "document",
        "workflow",
        "contact",
        "ledger_account",
        "value",
        "view_on_moneybird",
    ]

    readonly_fields = (
        "date",
        "description",
        "document",
        "workflow",
        "contact",
        "ledger_account",
        "value",
        "view_on_moneybird",
    )


class SalesAndPurchaseJournalDocumentLineInline(JournalDocumentLineInline):
    def get_queryset(self, request):
        return (
            super()
            .get_queryset(request)
            .exclude(
                document_line__ledger_account__account_type=LedgerAccountType.REVENUE,
                document_line__ledger_account__is_sales=False,
            )
            .exclude(
                document_line__ledger_account__account_type=LedgerAccountType.EXPENSES,
                document_line__ledger_account__is_purchase=False,
            )
        )


class NonSalesRevenueDocumentLineInline(JournalDocumentLineInline):
    def get_queryset(self, request):
        return (
            super()
            .get_queryset(request)
            .filter(
                document_line__ledger_account__account_type=LedgerAccountType.REVENUE,
                document_line__ledger_account__is_sales=False,
            )
        )


class NonPurchaseExpenseDocumentLineInline(JournalDocumentLineInline):
    def get_queryset(self, request):
        return (
            super()
            .get_queryset(request)
            .filter(
                document_line__ledger_account__account_type=LedgerAccountType.EXPENSES,
                document_line__ledger_account__is_purchase=False,
            )
        )


class EstimateDocumentLineInline(DocumentLineInline):
    model = AssetOnEstimateDocumentLine

    fields = [
        "date",
        "description",
        "document",
        "document_state",
        "workflow",
        "contact",
        "ledger_account",
        "value",
        "view_on_moneybird",
    ]

    readonly_fields = (
        "date",
        "description",
        "document",
        "document_state",
        "workflow",
        "contact",
        "ledger_account",
        "value",
        "view_on_moneybird",
    )

    @admin.display(description=_("Document state"))
    def document_state(self, obj):
        return obj.document_line.document.state


class RecurringSalesDocumentLineInline(DocumentLineInline):
    model = AssetOnRecurringSalesInvoiceDocumentLine

    fields = [
        "date",
        "description",
        "document",
        "active",
        "workflow",
        "contact",
        "ledger_account",
        "value",
        "view_on_moneybird",
    ]

    readonly_fields = (
        "date",
        "description",
        "document",
        "active",
        "workflow",
        "contact",
        "ledger_account",
        "value",
        "view_on_moneybird",
    )

    @admin.display(description=_("Active"), boolean=True)
    def active(self, obj):
        return obj.document_line.document.active


class AssetOnJournalDocumentLineInline(admin.TabularInline):
    model = AssetOnJournalDocumentLine
    extra = 0
    autocomplete_fields = ["asset"]


class AssetOnEstimateDocumentLineInline(admin.TabularInline):
    model = AssetOnEstimateDocumentLine
    extra = 0
    autocomplete_fields = ["asset"]


class AssetOnRecurringSalesInvoiceDocumentLineInline(admin.TabularInline):
    model = AssetOnRecurringSalesInvoiceDocumentLine
    extra = 0
    autocomplete_fields = ["asset"]

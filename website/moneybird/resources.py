from moneybird.resource_types import (
    MoneybirdResourceTypeWithDocumentLines,
    MoneybirdResourceType,
    SynchronizableMoneybirdResourceType,
    MoneybirdResource,
    get_moneybird_resource_type_for_entity,
)


class SalesInvoiceResourceType(MoneybirdResourceTypeWithDocumentLines):
    entity_type = "SalesInvoice"
    entity_type_name = "sales_invoice"
    api_path = "sales_invoices"
    document_lines_resource_data_name = "details"
    document_lines_attributes_name = "details_attributes"


class PurchaseInvoiceDocumentResourceType(MoneybirdResourceTypeWithDocumentLines):
    entity_type = "PurchaseInvoice"
    entity_type_name = "purchase_invoice"
    api_path = "documents/purchase_invoices"
    document_lines_resource_data_name = "details"
    document_lines_attributes_name = "details_attributes"


class ReceiptResourceType(MoneybirdResourceTypeWithDocumentLines):
    entity_type = "Receipt"
    entity_type_name = "receipt"
    api_path = "documents/receipts"
    document_lines_resource_data_name = "details"
    document_lines_attributes_name = "details_attributes"


class GeneralJournalDocumentResourceType(MoneybirdResourceTypeWithDocumentLines):
    entity_type = "GeneralJournalDocument"
    entity_type_name = "general_journal_document"
    api_path = "documents/general_journal_documents"
    document_lines_resource_data_name = "general_journal_document_entries"
    document_lines_attributes_name = "general_journal_document_entries_attributes"


class TypelessDocumentsResourceType(SynchronizableMoneybirdResourceType):
    entity_type = "TypelessDocument"
    entity_type_name = "typeless_document"
    api_path = "documents/typeless_documents"


class EstimateResourceType(MoneybirdResourceTypeWithDocumentLines):
    entity_type = "Estimate"
    entity_type_name = "estimate"
    api_path = "estimates"
    document_lines_resource_data_name = "details"
    document_lines_attributes_name = "details_attributes"


class RecurringSalesInvoiceResourceType(MoneybirdResourceTypeWithDocumentLines):
    entity_type = "RecurringSalesInvoice"
    entity_type_name = "recurring_sales_invoice"
    api_path = "recurring_sales_invoices"
    document_lines_resource_data_name = "details"
    document_lines_attributes_name = "details_attributes"

    @classmethod
    def create_from_moneybird(cls, resource_data: MoneybirdResource):
        obj = super().create_from_moneybird(resource_data)
        subscription = resource_data.get("subscription", None)
        if subscription:
            resource_type = get_moneybird_resource_type_for_entity("Subscription")
            resource_type.get_or_create_from_moneybird_data(
                subscription["id"], subscription
            )
        return obj


class ContactResourceType(SynchronizableMoneybirdResourceType):
    entity_type = "Contact"
    entity_type_name = "contact"
    api_path = "contacts"

    # TODO request moneybird payments mandate data


class ProductResourceType(MoneybirdResourceType):
    entity_type = "Product"
    entity_type_name = "product"
    api_path = "products"
    paginated = True
    pagination_size = 10


class ProjectResourceType(MoneybirdResourceType):
    entity_type = "Project"
    entity_type_name = "project"
    api_path = "projects"
    paginated = True
    pagination_size = 25

    @classmethod
    def get_all_resources_api_endpoint_params(cls):
        params = super().get_all_resources_api_endpoint_params()
        if params is None:
            params = {}
        params["state"] = "all"
        return params


class LedgerAccountResourceType(MoneybirdResourceType):
    entity_type = "LedgerAccount"
    entity_type_name = "ledger_account"
    api_path = "ledger_accounts"


class IdentityResourceType(MoneybirdResourceType):
    entity_type = "Identity"
    entity_type_name = "identity"
    api_path = "identities"


class TimeEntriesResourceType(MoneybirdResourceType):
    entity_type = "TimeEntry"
    entity_type_name = "time_entry"
    api_path = "time_entries"


class SubscriptionResourceType(MoneybirdResourceType):
    entity_type = "Subscription"
    entity_type_name = "subscription"
    api_path = "subscriptions"
    can_do_full_sync = False


class WorkflowResourceType(MoneybirdResourceType):
    entity_type = "Workflow"
    entity_type_name = "workflow"
    api_path = "workflows"
    can_write = False
    can_delete = False


class TaxRateResourceType(MoneybirdResourceType):
    entity_type = "TaxRate"
    entity_type_name = "tax_rate"
    api_path = "tax_rates"
    can_write = False
    can_delete = False


class UserResourceType(MoneybirdResourceType):
    entity_type = "User"
    entity_type_name = "user"
    api_path = "users"
    can_write = False
    can_delete = False


class VerificationResourceType(MoneybirdResourceType):
    entity_type = "Verification"
    entity_type_name = "verification"
    api_path = "verifications"
    can_write = False
    can_delete = False


class FinancialAccountResourceType(MoneybirdResourceType):
    entity_type = "FinancialAccount"
    entity_type_name = "financial_account"
    api_path = "financial_accounts"
    can_write = False
    can_delete = False


class DocumentStyleResourceType(MoneybirdResourceType):
    entity_type = "DocumentStyle"
    entity_type_name = "document_style"
    api_path = "document_styles"
    can_write = False
    can_delete = False


class CustomFieldsResourceType(MoneybirdResourceType):
    entity_type = "CustomField"
    entity_type_name = "custom_field"
    api_path = "custom_fields"
    can_write = False
    can_delete = False


class AdministrationsResourceType(MoneybirdResourceType):
    entity_type = "Administration"
    entity_type_name = "administration"
    api_path = "administrations"
    can_write = False
    can_delete = False

    # TODO this has a different endpoint than the other resources


# TODO contact people, mandates, is per contact
# TODO financial mutations
# TODO external sales invoice, heeft geen synchronization endpoint, wel document lines

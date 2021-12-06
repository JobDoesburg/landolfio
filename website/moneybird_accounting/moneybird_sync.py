import logging

from django.conf import settings
from moneybird import MoneyBird, TokenAuthentication



class MoneyBirdAPITalker:
    _logger = logging.getLogger("django.moneybird")

    _token = settings.MONEYBIRD_API_TOKEN
    _administration_id = settings.MONEYBIRD_ADMINISTRATION_ID
    _moneybird = MoneyBird(TokenAuthentication(_token))


    _taxable_stock_ledger_id = "340246538381952245"
    _margin_stock_ledger_id = "340246234795083709"
    _taxable_stock_value_ledger_id = "340246576039462518"
    _margin_stock_value_ledger_id = "340245783921034390"
    _margin_sales_ledger_id = "340245854757586711"
    _taxable_sales_ledger_id = "340246558119298417"
    _non_fiscal_amortization_ledger_id = "340246156081628510"
    _fiscal_amortization_ledger_id = "340246156081628510"

    @property
    def moneybird(self):
        """An Moneybird API instance (can be adapted to support API sessions)."""
        return self._moneybird

    @property
    def administration_id(self):
        """The administration_id to work with."""
        return self._administration_id

    def get_contacts(self):
        return self.moneybird.get("contacts", self.administration_id)

    def get_document_styles(self):
        return self.moneybird.get("document_styles", self.administration_id)

    def get_general_documents(self):
        return self.moneybird.get("documents/general_documents", self.administration_id)

    def get_purchase_invoices(self):
        return self.moneybird.get("documents/purchase_invoices", self.administration_id)

    def get_receipts(self):
        return self.moneybird.get("documents/receipts", self.administration_id)

    def get_general_journal_documents(self):
        return self.moneybird.get("documents/general_journal_documents", self.administration_id)

    def get_typeless_documents(self):
        return self.moneybird.get("documents/typeless_documents", self.administration_id)

    def get_estimates(self):
        return self.moneybird.get("estimates", self.administration_id)

    def get_external_sales_invoices(self):
        return self.moneybird.get("external_sales_invoices", self.administration_id)

    def get_financial_accounts(self):
        return self.moneybird.get("financial_accounts", self.administration_id)

    def get_financial_mutations(self):
        return self.moneybird.get("financial_mutations", self.administration_id)

    def get_ledger_accounts(self):
        return self.moneybird.get("ledger_accounts", self.administration_id)

    def get_products(self, id=None):
        if id:
            return self.moneybird.get(f"products/{id}", self.administration_id)
        return self.moneybird.get("products", self.administration_id)

    def get_identities(self):
        return self.moneybird.get("identities", self.administration_id)

    def get_projects(self, id=None):
        if id:
            return self.moneybird.get(f"projects/{id}", self.administration_id)
        return self.moneybird.get("projects", self.administration_id)

    def get_recurring_sales_invoices(self, id=None):
        if id:
            return self.moneybird.get(f"recurring_sales_invoices/{id}", self.administration_id)
        return self.moneybird.get("recurring_sales_invoices", self.administration_id)

    def get_sales_invoices(self):
        return self.moneybird.get("sales_invoices", self.administration_id)

    def get_subscriptions(self):
        return self.moneybird.get("subscriptions", self.administration_id)

    def get_tax_rates(self):
        return self.moneybird.get("tax_rates", self.administration_id)

    def get_time_entries(self):
        return self.moneybird.get("time_entries", self.administration_id)

    def get_users(self):
        return self.moneybird.get("users", self.administration_id)

    def get_verifications(self):
        return self.moneybird.get("verifications", self.administration_id)

    def get_webhooks(self):
        return self.moneybird.get("webhooks", self.administration_id)

    def get_workflows(self):
        return self.moneybird.get("workflows", self.administration_id)


    def get_purchase_invoice_rows_for_keyword(self, keyword):
        invoices = self.get_purchase_invoices()
        for invoice in invoices:
            details = invoice["details"]
            for row in details:
                if keyword in row["description"]:
                    yield row["total_price_excl_tax_with_discount_base"], row["ledger_account_id"]



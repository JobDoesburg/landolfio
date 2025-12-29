"""Test the accounting models."""

import datetime

from django.test import TestCase

from accounting.moneybird import DocKind
from inventory.models import Asset, Collection

from .models import Document


class TestGetDocumentUrl(TestCase):
    """Test the document moneybird property url."""

    # pylint: disable=protected-access

    def test_purchase_invoice(self):
        """Test the _build_document_url function with a purchase invoice."""
        doc_id = 340247496762590378
        adm_id = 293065149189719909
        doc_data = {"id": str(doc_id), "administration_id": str(adm_id)}

        doc = Document.objects.create(
            moneybird_id=doc_id, moneybird_json=doc_data, kind=DocKind.PURCHASE_INVOICE
        )
        self.assertEqual(
            doc.moneybird_url,
            "https://moneybird.com/293065149189719909/documents/340247496762590378",
        )

    def test_sales_invoice(self):
        """Test the _build_document_url function with a sales invoice."""
        doc_id = 340247835118142508
        adm_id = 293065149189719909
        doc_data = {"id": str(doc_id), "administration_id": str(adm_id)}

        doc = Document.objects.create(
            moneybird_id=doc_id, moneybird_json=doc_data, kind=DocKind.SALES_INVOICE
        )
        self.assertEqual(
            doc.moneybird_url,
            "https://moneybird.com/293065149189719909"
            "/sales_invoices/340247835118142508",
        )


class AccountingModelTest(TestCase):
    """Test cases for accounting models."""

    DATE_TEST = datetime.date(2022, 1, 25)

    def setUp(self):
        """Set up the test case."""
        Collection.objects.create(id=1, name="Privé")
        Asset.objects.create(
            id="C7801",
            asset_type="Violin",
            size="7/8",
            collection=Collection.objects.get(id=1),
            listing_price=750,
            stock_price="1200",
            purchasing_value=200.0,
        )
        Document.objects.create(kind="IV", moneybird_json='{"id":5}', moneybird_id=5)
        Document.objects.create(kind="RC", moneybird_json='{"id":5}', moneybird_id=5)

    @staticmethod
    def test_get_document():
        """Test the retrieval of a document."""
        _document = Document.objects.get(kind="IV")

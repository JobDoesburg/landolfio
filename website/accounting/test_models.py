import datetime

from accounting.models import Asset
from django.test import TestCase

from .models import Invoice
from .models import Receipt

# pylint: disable=no-member
class AccountingTestCase(TestCase):
    """Test cases for accounting models."""

    def setUp(self):
        """Set up the test case."""
        testdate = datetime.date(2022, 1, 25)
        Asset.objects.create(
            old_id="C7801",
            asset_type="Violin",
            size="7/8",
            collection="Zakelijk",
            listing_price=750,
            stock_price="1200",
            purchasing_value=200.0,
            margin=True,
        )
        Invoice.objects.create(
            asset=Asset.objects.get(old_id="C7801"),
            json_MB="",
            date=testdate,
            amount=1200,
        )
        Receipt.objects.create(
            asset=Asset.objects.get(old_id="C7801"),
            json_MB="",
            date=testdate,
            amount=750,
        )

    def test_invoice_attributes(self):
        """Test the functionality of an invoice."""
        testdate = datetime.date(2022, 1, 25)
        invoice = Invoice.objects.get(amount=1200)
        self.assertEqual(invoice.date, testdate)
        self.assertEqual(invoice.amount, 1200)

    def test_receipt_attributes(self):
        """Test the functionality of a receipt."""
        testdate = datetime.date(2022, 1, 25)
        receipt = Receipt.objects.get(amount=750)
        self.assertEqual(receipt.date, testdate)
        self.assertEqual(receipt.amount, 750)

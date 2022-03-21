import datetime

from assets.models import Asset
from django.test import TestCase

from .models import Document
from .models import DocumentLine


# pylint: disable=no-member
class AccountingTestCase(TestCase):
    """Test cases for accounting models."""

    DATE_TEST = datetime.date(2022, 1, 25)

    def setUp(self):
        """Set up the test case."""
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
        DocumentLine.objects.create(
            json_MB="", asset=Asset.objects.get(old_id="C7801"), price="1200"
        )
        Document.objects.create(
            kind="IV",
            json_MB="",
            date=self.DATE_TEST,
        )
        Document.objects.create(
            kind="RC",
            json_MB="",
            date=self.DATE_TEST,
        )

    def test_document_attributes(self):
        """Test the functionality of a document."""
        document = Document.objects.get(kind="IV")
        self.assertEqual(document.date, self.DATE_TEST)

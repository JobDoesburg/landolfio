"""Test the accounting models."""
import datetime

from assets.models import Asset
from django.test import TestCase

from .models import Document


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
        Document.objects.create(
            kind="IV",
            json_MB="",
        )
        Document.objects.create(
            kind="RC",
            json_MB="",
        )

    @staticmethod
    def test_get_document():
        """Test the retrieval of a document."""
        _document = Document.objects.get(kind="IV")

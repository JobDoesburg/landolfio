"""Test the accounting models."""
import datetime

from django.test import TestCase
from inventory.models import Asset
from inventory.models import Collection

from .models import Document


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
        Document.objects.create(kind="IV", json_MB='{"id":5}', id_MB=5)
        Document.objects.create(kind="RC", json_MB='{"id":5}', id_MB=5)

    @staticmethod
    def test_get_document():
        """Test the retrieval of a document."""
        _document = Document.objects.get(kind="IV")

"""Test the asset-models."""
from django.test import TestCase

from .models import Asset
from .models import Collection


class AssetModelTest(TestCase):
    """Test cases for the Asset model."""

    fixtures = ["assets"]

    def setUp(self):
        """Set up the test case."""
        collection = Collection.objects.create(id=1, name="Privé")
        Asset.objects.create(
            id="C7800",
            asset_type="Violin",
            size="7/8",
            collection=collection,
            listing_price="750",
            stock_price="1200",
            purchasing_value="200",
        )

    def test_assets_attributes(self):
        """Test the functionality of an asset."""
        asset = Asset.objects.get(id="C7800")
        self.assertEqual(asset.id, "C7800")
        self.assertEqual(asset.asset_type, "Violin")
        self.assertEqual(asset.size, "7/8")
        self.assertEqual(asset.collection, Collection.objects.get(id=1))
        self.assertEqual(asset.listing_price, 750)
        self.assertEqual(asset.stock_price, 1200)
        self.assertEqual(asset.purchasing_value, 200)

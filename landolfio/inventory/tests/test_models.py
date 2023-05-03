"""Test the asset-models."""
from django.test import TestCase

from website.inventory.models import Collection, Asset


class AssetModelTest(TestCase):
    """Test cases for the Asset model."""

    fixtures = ["assets"]

    def setUp(self):
        """Set up the test case."""
        collection = Collection.objects.create(id=2, name="Privé")
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
        asset = Asset.objects.get(name="C7800")
        self.assertEqual(asset.name, "C7800")
        self.assertEqual(asset.asset_type, "Violin")
        self.assertEqual(asset.size, "7/8")
        self.assertEqual(asset.collection, Collection.objects.get(id=2))
        self.assertEqual(asset.listing_price, 750)
        self.assertEqual(asset.stock_price, 1200)
        self.assertEqual(asset.purchasing_value, 200)

"""Test the asset-models."""
import datetime

from django.test import TestCase

from .models import Asset
from .models import AssetState


class AssetTestCase(TestCase):
    """Test cases for the Asset model."""

    fixtures = ["assets"]

    def setUp(self):
        """Set up the test case."""
        asset = Asset.objects.create(
            old_id="C7800",
            asset_type="Violin",
            size="7/8",
            collection="Zakelijk",
            listing_price="750",
            stock_price="1200",
            purchasing_value="200",
            margin=True,
        )
        AssetState.objects.create(
            asset=asset,
            date=datetime.date(2022, 1, 25),
            state="purchased",
            room="Room A",
            closet="Closet B",
            external="External C",
        )

    def test_assets_attributes(self):
        """Test the functionality of an asset."""
        asset = Asset.objects.get(old_id="C7800")
        self.assertEqual(asset.old_id, "C7800")
        self.assertEqual(asset.asset_type, "Violin")
        self.assertEqual(asset.size, "7/8")
        self.assertEqual(asset.collection, "Zakelijk")
        self.assertEqual(asset.listing_price, 750)
        self.assertEqual(asset.stock_price, 1200)
        self.assertEqual(asset.purchasing_value, 200)
        self.assertEqual(asset.margin, True)

    def test_asset_state_relation(self):
        """Test ability to retrieve AssetStates from Asset."""
        asset = Asset.objects.get(old_id="C7800")
        asset_state = AssetState.objects.get(asset=asset)
        self.assertEqual(asset_state.date, datetime.date(2022, 1, 25))
        self.assertEqual(asset_state.state, "purchased")
        self.assertEqual(asset_state.room, "Room A")
        self.assertEqual(asset_state.closet, "Closet B")
        self.assertEqual(asset_state.external, "External C")

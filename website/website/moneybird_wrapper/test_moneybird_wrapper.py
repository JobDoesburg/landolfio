"""Test the MoneyBirdWrapper."""
import unittest
from unittest.mock import patch


class MoneyBirdMock:
    """Mock version of the MoneyBird API."""

    # pylint: disable=too-few-public-methods

    def __init__(self, authentication):
        """Initialize a new MoneyBirdMock."""
        self.authentication = authentication

    def get(self, resource_path: str, administration_id: int = None):
        """Mock a GET request for the Moneybird API."""
        # pylint: disable=unused-argument,no-self-use
        if resource_path == "administrations":
            return [{"id": "0"}]

        if resource_path == "documents/purchase_invoices/synchronization":
            return {}

        if resource_path == "documents/receipts/synchronization":
            return {}

        # Incorrect path was used
        raise MoneyBirdMock.NotFound

    def post(self, resource_path: str, data: dict, administration_id: int = None):
        """Mock a POST request for the Moneybird API."""
        # pylint: disable=unused-argument,no-self-use
        if resource_path == "documents/purchase_invoices/synchronization":
            return {}

        if resource_path == "documents/receipts/synchronization":
            return {}

        # Incorrect path was used
        raise MoneyBirdMock.NotFound

    class NotFound(Exception):
        """Exception for requests to non-existing resource paths."""


class MoneybirdWrapperTest(unittest.TestCase):
    """Class to test the MoneyBirdWrapper."""

    def test_load_purchase_invoices(self):
        """Test loading purchase invoices."""
        with patch("moneybird.MoneyBird", new=MoneyBirdMock):
            # pylint: disable=import-outside-toplevel
            from .moneybird_wrapper import MoneyBirdWrapper

            wrapper = MoneyBirdWrapper("mock_key")
            self.assertListEqual(
                wrapper.load_purchase_invoices(),
                [],
                "Incorrect purchase invoices response",
            )

    def test_load_receipts(self):
        """Test loading receipts."""
        with patch("moneybird.MoneyBird", new=MoneyBirdMock):
            # pylint: disable=import-outside-toplevel
            from .moneybird_wrapper import MoneyBirdWrapper

            wrapper = MoneyBirdWrapper("mock_key")
            self.assertListEqual(
                wrapper.load_receipts(), [], "Incorrect receipts response"
            )

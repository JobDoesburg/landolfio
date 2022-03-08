"""Test the MoneyBirdWrapper."""
import unittest
from unittest.mock import patch


def make_moneybird_mock(purchase_invoices, receipts):
    """Create a Mock version of the Moneybird API with given purchase invoices and receipts."""

    class MoneyBirdMock:
        """Mock version of the MoneyBird API."""

        # pylint: disable=too-few-public-methods

        def __init__(self, authentication):
            """Initialize a new MoneyBirdMock."""
            self.authentication = authentication
            self.purchase_invoices = purchase_invoices
            self.receipts = receipts

        def get(self, resource_path: str, administration_id: int = None):
            """Mock a GET request for the Moneybird API."""
            # pylint: disable=unused-argument
            if resource_path == "administrations":
                return [{"id": "0"}]

            if resource_path == "documents/purchase_invoices/synchronization":
                return [
                    {"id": invoice["id"], "version": invoice["version"]}
                    for invoice in self.purchase_invoices
                ]

            if resource_path == "documents/receipts/synchronization":
                return [
                    {"id": receipt["id"], "version": receipt["version"]}
                    for receipt in self.receipts
                ]

            # Incorrect path was used
            raise MoneyBirdMock.NotFound

        def post(self, resource_path: str, data: dict, administration_id: int = None):
            """Mock a POST request for the Moneybird API."""
            # pylint: disable=unused-argument
            if resource_path == "documents/purchase_invoices/synchronization":
                ids = data["ids"]
                return filter(
                    lambda invoice: invoice["id"] in ids, self.purchase_invoices
                )

            if resource_path == "documents/receipts/synchronization":
                ids = data["ids"]
                return filter(lambda receipt: receipt["id"] in ids, self.receipts)

            # Incorrect path was used
            raise MoneyBirdMock.NotFound

        class NotFound(Exception):
            """Exception for requests to non-existing resource paths."""

    return MoneyBirdMock


class MoneybirdWrapperTest(unittest.TestCase):
    """Class to test the MoneyBirdWrapper."""

    def test_load_purchase_invoices(self):
        """Test loading purchase invoices."""
        purchase_invoices = [{"id": "1", "version": 3}, {"id": "2", "version": 7}]
        receipts = [{"id": "112", "version": 2}, {"id": "22", "version": 5}]
        with patch(
            "moneybird.MoneyBird", new=make_moneybird_mock(purchase_invoices, receipts)
        ):
            # pylint: disable=import-outside-toplevel
            from .moneybird_wrapper import MoneyBirdWrapper

            wrapper = MoneyBirdWrapper("mock_key")
            self.assertListEqual(
                wrapper.load_purchase_invoices(),
                purchase_invoices,
                "Incorrect purchase invoices response",
            )

    def test_load_receipts(self):
        """Test loading receipts."""
        purchase_invoices = [{"id": "1", "version": 3}, {"id": "2", "version": 7}]
        receipts = [{"id": "112", "version": 2}, {"id": "22", "version": 5}]
        with patch(
            "moneybird.MoneyBird", new=make_moneybird_mock(purchase_invoices, receipts)
        ):
            # pylint: disable=import-outside-toplevel
            from .moneybird_wrapper import MoneyBirdWrapper

            wrapper = MoneyBirdWrapper("mock_key")
            self.assertListEqual(
                wrapper.load_receipts(),
                receipts,
                "Incorrect receipts response",
            )

"""Tests for the inventory Admin interface."""
from accounting.models import Document
from accounting.models import DocumentLine
from accounting.models import Ledger
from accounting.moneybird import DocKind
from django.contrib.admin import AdminSite
from django.shortcuts import render
from django.test import TestCase
from inventory.admin import AssetAdmin
from inventory.models import Asset


class MockSuperUser:
    """A mock version of a Django super user."""

    def has_perm(self, _perm, _obj=None):
        # pylint: disable=no-self-use
        """
        Return true iff the user has a certain permission.

        This is the superuser, so it has all permissions.
        """
        return True

    def is_active(self):
        # pylint: disable=no-self-use
        """
        Return true iff the user is active.

        This is a mock user, so we say that this user is always active.
        """
        return True

    def is_staff(self):
        # pylint: disable=no-self-use
        """
        Return true iff the user is staff.

        This is the superuser, so it is always staff.
        """
        return True


class MockRequest:
    # pylint: disable=too-few-public-methods
    """A mock version of a Django Get request."""

    def __init__(self, method="GET"):
        """Create a mock request."""
        # pylint: disable=invalid-name

        self.method = method
        self.COOKIES = {}
        self.POST = {}
        self.GET = {}
        self.META = {"SCRIPT_NAME": None}
        self.user = MockSuperUser()
        self.resolver_match = None


class AssetAdminTest(TestCase):
    """Test the Asset admin interface."""

    fixtures = ["assets"]

    def setUp(self):
        """Set up the tests."""
        self.site = AdminSite()

    def test_changeform_view_without_documents(self):
        """Rendering the changeform_view must not raise any exceptions."""
        asset_admin = AssetAdmin(Asset, self.site)
        request = MockRequest()
        template_response = asset_admin.changeform_view(request)

        render(
            request,
            template_response.template_name,
            context=template_response.context_data,
        )

    def test_changeform_view_with_documens(self):
        """Rendering the changeform_view must not raise any exceptions."""
        asset = Asset.objects.get(id="C44103")

        some_big_number = 35956490534690546
        some_other_number = 9650794650946
        test_doc = Document.objects.create(
            moneybird_id=some_big_number,
            kind=DocKind.PURCHASE_INVOICE,
            moneybird_json={
                "administration_id": some_other_number,
                "id": some_big_number,
            },
        )
        test_ledger = Ledger.objects.create(moneybird_id=42)
        _test_doc_line = DocumentLine.objects.create(
            asset=asset,
            moneybird_json={},
            document=test_doc,
            ledger=test_ledger,
            price=10,
        )

        asset_admin = AssetAdmin(Asset, self.site)
        request = MockRequest()
        template_response = asset_admin.changeform_view(request, object_id=asset.id)

        render(
            request,
            template_response.template_name,
            context=template_response.context_data,
        )

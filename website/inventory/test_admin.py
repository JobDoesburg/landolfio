"""Tests for the inventory Admin interface."""
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

    def setUp(self):
        """Set up the tests."""
        self.site = AdminSite()

    def test_changeform_view(self):
        """Rendering the changeform_view must not raise any exceptions."""
        asset_admin = AssetAdmin(Asset, self.site)
        request = MockRequest()
        template_response = asset_admin.changeform_view(request)

        render(
            request,
            template_response.template_name,
            context=template_response.context_data,
        )

from unittest import mock

from django.test import TestCase, override_settings

from moneybird.webhooks.events import WebhookEvent
from moneybird.webhooks.processing import process_webhook_payload


@override_settings(MONEYBIRD_WEBHOOK_ID="987654321")
@override_settings(MONEYBIRD_WEBHOOK_TOKEN="aBcDeFgHiJkLmNoPqRsTuVwXyZ")
@override_settings(MONEYBIRD_ADMINISTRATION_ID=1234567890)
class MoneybirdWebhookProcessingTest(TestCase):
    def setUp(self):
        self.payload = {
            "administration_id": "1234567890",
            "webhook_id": "987654321",
            "webhook_token": "aBcDeFgHiJkLmNoPqRsTuVwXyZ",
            "entity_type": "SalesInvoice",
            "entity_id": "116015245643744263",
            "state": "new_state",
            "action": "sales_invoice_created",
            "entity": {"id": "116015245643744263", "data": "test"},
        }

    @mock.patch("moneybird.webhooks.processing.get_moneybird_resource_type_for_entity")
    def test_valid_payload(self, get_resource_type):
        resource_type = get_resource_type.return_value
        process_webhook_payload(self.payload)
        get_resource_type.assert_called_once_with("SalesInvoice")
        resource_type.process_webhook_event.assert_called_once_with(
            self.payload["entity_id"],
            self.payload["entity"],
            WebhookEvent.SALES_INVOICE_CREATED,
        )

    @mock.patch("moneybird.webhooks.processing.get_moneybird_resource_type_for_entity")
    def test_test_webhook_is_ignored(self, get_resource_type):
        self.payload["action"] = "test_webhook"
        process_webhook_payload(self.payload)
        get_resource_type.assert_not_called()

    @mock.patch("moneybird.webhooks.processing.get_moneybird_resource_type_for_entity")
    def test_invalid_credentials(self, get_resource_type):
        for field, value in [
            ("webhook_id", "invalid"),
            ("webhook_token", "invalid"),
            ("administration_id", "999999"),
        ]:
            with self.subTest(field=field):
                payload = dict(self.payload, **{field: value})
                process_webhook_payload(payload)
                get_resource_type.assert_not_called()

    @mock.patch("moneybird.webhooks.processing.get_moneybird_resource_type_for_entity")
    def test_invalid_event(self, get_resource_type):
        self.payload["action"] = "invalid"
        process_webhook_payload(self.payload)
        get_resource_type.assert_not_called()

    @mock.patch(
        "moneybird.webhooks.processing.get_moneybird_resource_type_for_entity",
        return_value=None,
    )
    def test_unregistered_entity_type(self, get_resource_type):
        process_webhook_payload(self.payload)
        get_resource_type.assert_called_once_with("SalesInvoice")

    @mock.patch("moneybird.webhooks.processing.get_moneybird_resource_type_for_entity")
    def test_company_assets_sub_entity_routes_to_asset(self, get_resource_type):
        asset_resource_type = mock.Mock()
        get_resource_type.side_effect = [None, asset_resource_type]
        self.payload["action"] = "company_assets_disposal_created"
        self.payload["entity_type"] = "CompanyAssets::Disposal"
        self.payload["entity"] = {"id": "1", "asset_id": "42"}
        process_webhook_payload(self.payload)
        get_resource_type.assert_has_calls(
            [
                mock.call("CompanyAssets::Disposal"),
                mock.call("company_assets_asset"),
            ]
        )
        asset_resource_type.process_webhook_event.assert_called_once_with(
            "42",
            {"id": "1", "asset_id": "42"},
            WebhookEvent.COMPANY_ASSETS_DISPOSAL_CREATED,
        )

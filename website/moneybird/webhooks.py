import logging

from django.conf import settings
from django.urls import reverse

from moneybird.administration import get_moneybird_administration
from moneybird.resource_types import (
    MoneybirdResource,
    get_moneybird_resource_type_for_webhook_entity,
)


def process_webhook_payload(payload: MoneybirdResource) -> None:
    if payload["webhook_id"] != settings.MONEYBIRD_WEBHOOK_ID:
        logging.warning("Received webhook with wrong id")
        return

    if payload["webhook_token"] != settings.MONEYBIRD_WEBHOOK_TOKEN:
        logging.warning("Received webhook with wrong token")
        return

    if int(payload["administration_id"]) != settings.MONEYBIRD_ADMINISTRATION_ID:
        logging.warning("Received webhook for wrong administration")
        return

    event = payload["action"]

    if event not in settings.MONEYBIRD_WEBHOOK_EVENTS:
        logging.warning("Received webhook with unknown event")
        return

    entity_type = payload["entity_type"]
    entity = payload["entity"]
    resource_type = get_moneybird_resource_type_for_webhook_entity(entity_type)

    if resource_type is None:
        logging.warning("Received webhook with unregistered entity type")
        return

    return resource_type.process_webhook_event(entity, event)


def get_webhook_receive_endpoint():
    if not settings.MONEYBIRD_WEBHOOK_SITE_DOMAIN:
        return None
    return settings.MONEYBIRD_WEBHOOK_SITE_DOMAIN + reverse("moneybird:webhook_receive")


def create_webhook():
    if settings.MONEYBIRD_WEBHOOK_SITE_DOMAIN.startswith("http://") and not (
        settings.DEBUG or settings.MONEYBIRD_WEBHOOK_ALLOW_INSECURE
    ):
        logging.warning("MONEYBIRD_WEBHOOK_SITE_DOMAIN is not secure")
        return None

    url = get_webhook_receive_endpoint()
    if not url:
        return

    events = settings.MONEYBIRD_WEBHOOK_EVENTS
    if events is None:
        logging.info("No events to register a webhook for.")
        return

    administration = get_moneybird_administration()
    return administration.post("webhooks", data={"url": url, "events": events})


def get_webhooks():
    administration = get_moneybird_administration()
    return administration.get("webhooks")


def delete_webhook(webhook_id):
    administration = get_moneybird_administration()
    return administration.delete(f"webhooks/{webhook_id}")

import logging

from moneybird.resource_types import (
    MoneybirdResource,
    get_moneybird_resource_type_for_entity,
)
from moneybird.settings import settings
from moneybird.webhooks.events import WebhookEvent


def process_webhook_payload(payload: MoneybirdResource) -> None:
    if payload["action"] == "test_webhook":
        logging.info(f"Received test webhook from Moneybird: {payload}")
        return

    if payload["webhook_id"] != settings.MONEYBIRD_WEBHOOK_ID:
        logging.warning("Received webhook with wrong id")
        raise ValueError("Received webhook with wrong id")

    if payload["webhook_token"] != settings.MONEYBIRD_WEBHOOK_TOKEN:
        logging.warning("Received webhook with wrong token")
        raise ValueError("Received webhook with wrong token")

    if int(payload["administration_id"]) != settings.MONEYBIRD_ADMINISTRATION_ID:
        logging.warning("Received webhook for wrong administration")
        raise ValueError("Received webhook for wrong administration")

    try:
        event = WebhookEvent(payload["action"])
    except ValueError:
        logging.warning("Received webhook with invalid event")
        raise ValueError("Received webhook with invalid event")

    entity_type = payload["entity_type"]
    entity_id = payload["entity_id"]
    entity_data = payload["entity"]
    resource_type = get_moneybird_resource_type_for_entity(entity_type)

    if resource_type is None:
        logging.warning("Received webhook with unregistered entity type")
        raise ValueError("Received webhook with unregistered entity type")

    logging.info(f"Received webhook {event} for {entity_type} {entity_id}: {entity_data}")

    return resource_type.process_webhook_event(entity_id, entity_data, event)

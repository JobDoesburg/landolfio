import logging

from moneybird.resource_types import (
    MoneybirdResource,
    get_moneybird_resource_type_for_entity,
)
from moneybird.settings import settings
from moneybird.webhooks.events import WebhookEvent


def process_webhook_payload(payload: MoneybirdResource) -> None:
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

    if event not in settings.MONEYBIRD_WEBHOOK_EVENTS:
        logging.warning("Received webhook with unknown event")
        raise ValueError("Received webhook with unknown event")

    entity_type = payload["entity_type"]
    entity = payload["entity"]
    resource_type = get_moneybird_resource_type_for_entity(entity_type)

    if resource_type is None:
        logging.warning("Received webhook with unregistered entity type")
        raise ValueError("Received webhook with unregistered entity type")

    return resource_type.process_webhook_event(entity, event)
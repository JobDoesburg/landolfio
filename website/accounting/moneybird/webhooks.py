import logging

from django.conf import settings
from django.urls import reverse

from accounting.moneybird.administration import get_moneybird_administration
from accounting.moneybird.resource_types import (
    MoneybirdResource,
    get_moneybird_resources,
)


def get_moneybird_resource_type_from_webhook_entity(entity_type):
    for resource_type in get_moneybird_resources():
        if resource_type.entity_type == entity_type:
            return resource_type


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
    resource_type = get_moneybird_resource_type_from_webhook_entity(entity_type)

    if resource_type is None:
        logging.warning("Received webhook with unregistered entity type")
        return

    return resource_type.process_webhook_event(entity, event)


def get_webhook_receive_endpoint():
    if not settings.MONEYBIRD_WEBHOOK_RECEIVE_ENDPOINT:
        return None
    return settings.MONEYBIRD_WEBHOOK_SITE_DOMAIN + reverse("moneybird:webhook_receive")


def create_webhook():
    if settings.MONEYBIRD_WEBHOOK_RECEIVE_ENDPOINT.startswith("http://") and not (
        settings.DEBUG or settings.MONEYBIRD_WEBHOOK_ALLOW_INSECURE
    ):
        logging.warning("MONEYBIRD_WEBHOOK_RECEIVE_ENDPOINT is not secure")
        return None

    url = get_webhook_receive_endpoint()
    if not url:
        return

    events = settings.MONEYBIRD_WEBHOOK_EVENTS
    administration = get_moneybird_administration()
    response = administration.post("webhooks", data={"url": url, "events": events})

    return response["id"], response["token"]
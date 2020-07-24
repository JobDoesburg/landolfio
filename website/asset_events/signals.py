from django.db.models.signals import pre_save, post_save
from django.dispatch import receiver

from asset_events.models import StatusChangingEvent


@receiver(post_save)
def update_asset_status(sender, instance, **kwargs):
    if not issubclass(sender, StatusChangingEvent):
        return

    sender.post_save(instance)

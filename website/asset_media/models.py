import os

from django.db import models
from django.db.models import CASCADE, SET_NULL
from django.utils import timezone

from asset_events.models import Event
from assets.models import Asset


class MediaSet(models.Model):
    class Meta:
        verbose_name = "media set"
        verbose_name_plural = "media sets"

    date = models.DateTimeField(default=timezone.now, blank=False, null=False)
    asset = models.ForeignKey(Asset, null=True, blank=True, on_delete=CASCADE)
    event = models.OneToOneField(Event, null=True, blank=True, on_delete=SET_NULL)
    remarks = models.TextField(null=True, blank=True)

    def __str__(self):
        if self.event:
            return f"{self.asset} media - {self.event}"
        return f"{self.asset} media"

    def save(self, force_insert=False, force_update=False, using=None, update_fields=None):
        if self.event:
            self.asset = self.event.asset
        super().save(force_insert, force_insert, update_fields, update_fields)


def get_upload_path(instance, filename):
    return f"asset_media/{instance.set.asset.number}/{instance.set.asset.number}_{timezone.now().strftime('%Y-%m-%d_%H-%M-%S')}_{filename}"


class MediaItem(models.Model):
    class Meta:
        verbose_name = "media item"
        verbose_name_plural = "media items"

    set = models.ForeignKey(MediaSet, null=False, blank=False, on_delete=CASCADE)
    media = models.FileField(null=False, blank=False, upload_to=get_upload_path)

    def __str__(self):
        return self.media.name

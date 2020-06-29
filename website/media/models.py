from django.db import models
from django.db.models import CASCADE

from assets.models import Asset


class MediaSet(models.Model):
    class Meta:
        verbose_name = "media set"
        verbose_name_plural = "media sets"

    created = models.DateTimeField(auto_created=True, blank=False, null=False)
    instrument = models.ForeignKey(Asset, null=True, blank=True, on_delete=CASCADE)
    remarks = models.TextField(null=True, blank=True)

    def __str__(self):
        return f"Media {self.instrument} ({self.created})"


class MediaItem(models.Model):
    class Meta:
        verbose_name = "media item"
        verbose_name_plural = "media items"

    set = models.ForeignKey(MediaSet, null=False, blank=False, on_delete=CASCADE)
    media = models.ImageField()
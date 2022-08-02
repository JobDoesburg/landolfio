from django.db import models
from django.db.models import PROTECT
from django.utils.translation import gettext_lazy as _


class AssetLocationGroup(models.Model):
    class Meta:
        verbose_name = "location group"
        verbose_name_plural = "location groups"
        ordering = ["order", "pk"]

    name = models.CharField(null=False, blank=False, max_length=20)
    order = models.PositiveSmallIntegerField(null=True, blank=True)

    def __str__(self):
        return self.name


class AssetLocation(models.Model):
    class Meta:
        verbose_name = "location"
        verbose_name_plural = "locations"
        ordering = ["location_group__order", "order", "pk"]

    name = models.CharField(null=False, blank=False, max_length=20)
    location_group = models.ForeignKey(
        AssetLocationGroup, blank=False, null=False, on_delete=PROTECT
    )
    order = models.PositiveSmallIntegerField(null=True, blank=True)

    def __str__(self):
        return f"{self.name} ({self.location_group})"

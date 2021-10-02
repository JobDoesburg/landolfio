from django.db import models
from django.db.models import PROTECT


class AssetLocationGroup(models.Model):
    class Meta:
        verbose_name = "location group"
        verbose_name_plural = "location groups"

    name = models.CharField(null=False, blank=False, max_length=20)

    def __str__(self):
        return self.name


class AssetLocation(models.Model):
    class Meta:
        verbose_name = "location"
        verbose_name_plural = "locations"

    name = models.CharField(null=False, blank=False, max_length=20)
    location_group = models.ForeignKey(AssetLocationGroup, blank=False, null=False, on_delete=PROTECT)

    def __str__(self):
        return f"{self.name} ({self.location_group})"


# TODO: improve this structure (make it more recursive?)
# TODO: location_category_set

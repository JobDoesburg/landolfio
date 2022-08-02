from django.db import models
from django.db.models import PROTECT
from django.utils.translation import gettext_lazy as _


class AssetLocationGroup(models.Model):
    class Meta:
        verbose_name = _("location group")
        verbose_name_plural = _("location groups")
        ordering = ["order", "pk"]

    name = models.CharField(null=False, blank=False, max_length=20, verbose_name=_("name"))
    order = models.PositiveSmallIntegerField(null=True, blank=True, verbose_name=_("order"))

    def __str__(self):
        return self.name


class AssetLocation(models.Model):
    class Meta:
        verbose_name = _("location")
        verbose_name_plural = _("locations")
        ordering = ["location_group__order", "order", "pk"]

    name = models.CharField(null=False, blank=False, max_length=20, verbose_name=_("name"))
    location_group = models.ForeignKey(
        AssetLocationGroup, blank=False, null=False, on_delete=PROTECT, verbose_name=_("location group")
    )
    order = models.PositiveSmallIntegerField(null=True, blank=True, verbose_name=_("order"))

    def __str__(self):
        return f"{self.name} ({self.location_group})"

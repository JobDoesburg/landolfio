from django.core.validators import validate_unicode_slug
from django.db import models
from django.utils.translation import gettext_lazy as _


class AssetCategory(models.Model):
    class Meta:
        verbose_name = "category"
        verbose_name_plural = "categories"
        ordering = ["order", "pk"]

    name = models.CharField(null=False, blank=False, max_length=20)
    name_singular = models.CharField(
        null=False, blank=False, max_length=20, validators=[validate_unicode_slug]
    )
    order = models.PositiveSmallIntegerField(null=True, blank=True)

    def __str__(self):
        return f"{self.name}"


class AssetSize(models.Model):
    class Meta:
        verbose_name = "size"
        verbose_name_plural = "sizes"
        ordering = ["order", "pk"]

    name = models.CharField(null=False, blank=False, max_length=20)
    categories = models.ManyToManyField(AssetCategory, blank=False)
    order = models.PositiveSmallIntegerField(null=True, blank=True)

    def __str__(self):
        return f"{self.name}"

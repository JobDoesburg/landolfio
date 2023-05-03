from django.core.validators import validate_unicode_slug
from django.db import models
from django.utils.translation import gettext_lazy as _


class Category(models.Model):
    class Meta:
        verbose_name = _("category")
        verbose_name_plural = _("categories")
        ordering = ["order", "pk"]

    name = models.CharField(
        null=False, blank=False, max_length=20, verbose_name=_("name")
    )
    name_singular = models.CharField(
        null=False,
        blank=False,
        max_length=20,
        validators=[validate_unicode_slug],
        verbose_name=_("name singular"),
    )
    order = models.PositiveSmallIntegerField(
        null=True, blank=True, verbose_name=_("order")
    )

    def __str__(self):
        return self.name


class Size(models.Model):
    class Meta:
        verbose_name = _("size")
        verbose_name_plural = _("sizes")
        ordering = ["order", "pk"]

    name = models.CharField(
        null=False, blank=False, max_length=20, verbose_name=_("name")
    )
    categories = models.ManyToManyField(
        Category, blank=False, verbose_name=_("categories")
    )
    order = models.PositiveSmallIntegerField(
        null=True, blank=True, verbose_name=_("order")
    )

    def __str__(self):
        return self.name

from django.db import models
from django.utils.translation import gettext_lazy as _


class Collection(models.Model):
    name = models.CharField(
        verbose_name=_("name"), max_length=200, unique=True
    )
    commerce = models.BooleanField(verbose_name=_("commerce"), default=True)
    order = models.PositiveSmallIntegerField(null=True, blank=True, verbose_name=_("order"))

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = _("collection")
        verbose_name_plural = _("collections")
        ordering = ["order", "pk"]

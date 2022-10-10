from django.db import models
from django.utils.translation import gettext_lazy as _

from moneybird import resources
from moneybird.models import (
    MoneybirdResourceModel,
)


class DocumentStyle(MoneybirdResourceModel):
    name = models.CharField(
        verbose_name=_("name"),
        max_length=100,
    )
    default = models.BooleanField(verbose_name=_("default"), default=True)

    class Meta:
        verbose_name = _("document style")
        verbose_name_plural = _("document styles")

    def __str__(self):
        return self.name


class DocumentStyleResourceType(resources.DocumentStyleResourceType):
    model = DocumentStyle

    @classmethod
    def get_model_kwargs(cls, resource_data):
        kwargs = super().get_model_kwargs(resource_data)
        kwargs["name"] = resource_data["name"]
        kwargs["default"] = resource_data["default"]
        return kwargs

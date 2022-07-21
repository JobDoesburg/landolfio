from django.db import models

from moneybird import resources
from moneybird.models import (
    MoneybirdResourceModel,
)


class DocumentStyle(MoneybirdResourceModel):
    name = models.CharField(
        max_length=100,
    )
    default = models.BooleanField(default=True)

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

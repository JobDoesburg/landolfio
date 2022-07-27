from django.db import models
from django.utils.translation import gettext as _

from moneybird import resources
from moneybird.models import (
    MoneybirdResourceModel,
)


class Project(MoneybirdResourceModel):
    name = models.CharField(
        max_length=255,
    )
    active = models.BooleanField(default=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = _("Project")
        verbose_name_plural = _("Projects")


class ProjectResourceType(resources.ProjectResourceType):
    model = Project

    @classmethod
    def get_model_kwargs(cls, resource_data):
        kwargs = super().get_model_kwargs(resource_data)
        kwargs["name"] = resource_data["name"]
        kwargs["active"] = resource_data["state"] == "active"
        return kwargs

    @classmethod
    def serialize_for_moneybird(cls, instance):
        data = super().serialize_for_moneybird(instance)
        data["name"] = instance.name
        return data

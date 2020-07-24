from django.db import models

from moneybird_accounting.models import MoneybirdReadWriteResourceModel


class Project(MoneybirdReadWriteResourceModel):
    class Meta:
        verbose_name = "project"
        verbose_name_plural = "projects"

    moneybird_resource_path_name = "projects"
    moneybird_resource_name = "project"

    moneybird_data_fields = [
        "name",
        "state",
    ]  # TODO add budget?

    name = models.CharField(blank=True, null=True, max_length=100)

    PROJECT_STATE_ACTIVE = "active"
    PROJECT_STATE_ARCHIVED = "archived"
    PROJECT_STATE_CHOICES = (
        (PROJECT_STATE_ACTIVE, "Active"),
        (PROJECT_STATE_ARCHIVED, "Archived"),
    )

    state = models.CharField(blank=True, null=True, choices=PROJECT_STATE_CHOICES, max_length=10)

    def __str__(self):
        return self.name

from django.db import models
from django.db.models import PROTECT

from moneybird_accounting.models import Contact


class MaintenanceProvider(models.Model):
    class Meta:
        verbose_name = "maintenance provider"
        verbose_name_plural = "maintenance providers"

    name = models.CharField(null=False, blank=False, max_length=150)
    contact = models.OneToOneField(Contact, null=True, blank=True, on_delete=PROTECT)

    def __str__(self):
        return self.name

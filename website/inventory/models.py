"""Asset models."""
from accounting.models import DocumentLine
from django.db import models
from django.urls import reverse
from django.utils.safestring import mark_safe
from django.utils.translation import gettext as _


STATES = (
    ("purchased", "purchased"),
    ("under_review", "under_review"),
    ("ready", "ready"),
    ("outgoing", "outgoing"),
    ("rented", "rented"),
    ("lent", "lent"),
    ("under_repair_internal", "under_repair_internal"),
    ("under_repair_external", "under_repair_external"),
    ("sold", "sold"),
    ("amortized", "amortized"),
)


class Asset(models.Model):
    """Class model for Assets."""

    id = models.CharField(verbose_name=_("ID"), max_length=200, primary_key=True)
    asset_type = models.CharField(verbose_name=_("Type"), max_length=200)
    size = models.CharField(verbose_name=_("Size"), max_length=200)
    collection = models.CharField(verbose_name=_("Collection"), max_length=200)
    listing_price = models.FloatField(verbose_name=_("Listing price"))
    stock_price = models.FloatField(verbose_name=_("Stock price"))
    purchasing_value = models.FloatField(verbose_name=_("Purchasing value"))
    margin = models.BooleanField(verbose_name=_("Margin"))
    remarks = models.TextField(
        verbose_name=_("Remarks"), max_length=1000, null=True, blank=True
    )

    def __str__(self):
        """Return Asset string."""
        return f"{self.asset_type} {self.size}"

    def related_documents(self):
        """Return all related Documents."""
        document_lines = DocumentLine.objects.filter(asset=self)
        documents = []

        for line in document_lines:
            document = line.document
            if document not in documents:
                documents.append(document)
        return documents

    @property
    def related_documents_links(self):
        """Return all related Documents as an HTML list of links."""
        result = ""
        for document in self.related_documents():
            result += get_object_admin_link(document) + "<br>"
        return mark_safe(result)


def get_object_admin_link(obj):
    """Return the admin HTML link of an object."""
    url = reverse(
        f"admin:{obj._meta.app_label}_{obj._meta.model_name}_change",
        args=(obj.pk,),
    )
    return f"<a href={url}>{str(obj)}</a>"


class AssetState(models.Model):
    """Class model for Asset States."""

    asset = models.ForeignKey(Asset, on_delete=models.CASCADE, verbose_name=_("Asset"))
    date = models.DateField(verbose_name=_("Date"))
    state = models.CharField(verbose_name=_("State"), choices=STATES, max_length=100)
    room = models.CharField(
        verbose_name=_("Room"), max_length=250, null=True, blank=True
    )
    closet = models.CharField(
        verbose_name=_("Closet"), max_length=250, null=True, blank=True
    )
    external = models.CharField(
        verbose_name=_("External"), max_length=250, null=True, blank=True
    )

    def __str__(self):
        """Return AssetState string."""
        return f"{self.asset.id} | {self.state}"

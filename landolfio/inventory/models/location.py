from django.db import models
from django.db.models import PROTECT, SET_NULL
from django.utils.translation import gettext_lazy as _


class Location(models.Model):
    class Meta:
        verbose_name = _("location")
        verbose_name_plural = _("locations")
        ordering = ["order", "pk"]

    name = models.CharField(
        null=False, blank=False, max_length=20, verbose_name=_("name")
    )
    parent = models.ForeignKey(
        "self",
        blank=True,
        null=True,
        on_delete=SET_NULL,
        related_name="children",
        verbose_name=_("parent location"),
    )
    display_as_root = models.BooleanField(
        default=False,
        verbose_name=_("display as root"),
        help_text=_(
            "Display this location as a root location (don't show parents in name)"
        ),
    )
    order = models.PositiveSmallIntegerField(
        null=True, blank=True, verbose_name=_("order")
    )

    def __str__(self):
        if self.display_as_root:
            return self.name
        if self.parent:
            return f"{self.parent.__str__()} › {self.name}"
        return self.name

    def get_full_path(self):
        """Returns the full path from root to this location."""
        if self.parent:
            return f"{self.parent.get_full_path()} › {self.name}"
        return self.name

    def get_ancestors(self, include_self=False):
        """Returns all ancestor locations."""
        ancestors = []
        if include_self:
            ancestors.append(self)
        current = self.parent
        while current:
            ancestors.insert(0, current)
            current = current.parent
        return ancestors

    def get_descendants(self, include_self=False):
        """Returns all descendant locations."""
        descendants = []
        if include_self:
            descendants.append(self)

        for child in self.children.all():
            descendants.append(child)
            descendants.extend(child.get_descendants(include_self=False))

        return descendants

    @property
    def is_root(self):
        """Returns True if this is a root location (no parent)."""
        return self.parent is None

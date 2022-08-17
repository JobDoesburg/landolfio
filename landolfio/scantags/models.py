import random

from stdnum.iso7064 import mod_37_36

from django.core.exceptions import ValidationError
from django.db import models
from django.utils.translation import gettext_lazy as _

from inventory.models.asset import Asset
from scantags import settings


def validate_iso7064_mod_37_36(value):
    """
    Validate that the given value is a valid ISO 7064 mod 37, 36 checksum.
    """
    if len(value) != settings.SCANTAGS_ID_LENGTH:
        raise ValidationError(
            _("Length must be {} characters.").format(settings.SCANTAGS_ID_LENGTH)
        )
    if not mod_37_36.is_valid(value, alphabet=settings.SCANTAGS_ALPHABET):
        raise ValidationError(
            _("%(value)s is not a valid mod 37, 36 checksum."),
            params={"value": value},
        )


def generate_new_id():
    existing_ids = ScanTag.objects.values_list("id", flat=True)
    while True:
        new_id = settings.SCANTAGS_PREFIX
        new_id += "".join(
            random.choices(
                settings.SCANTAGS_ALPHABET,
                k=settings.SCANTAGS_ID_LENGTH - 1 - len(new_id),
            )
        )
        new_id += mod_37_36.calc_check_digit(
            new_id, alphabet=settings.SCANTAGS_ALPHABET
        )
        if new_id not in existing_ids:
            return new_id


class ScanTag(models.Model):
    id = models.CharField(
        max_length=255,
        primary_key=True,
        validators=[validate_iso7064_mod_37_36],
        verbose_name=_("ID"),
        default=generate_new_id,
    )  # We don't hardcode the max_length of the id field, because we want to be able to set the length in the settings.
    asset = models.ForeignKey(
        Asset,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="scantags",
        verbose_name=_("Asset"),
    )

    def __str__(self):
        return self.id

    @classmethod
    def generate_new_id(cls):
        return generate_new_id()

    class Meta:
        verbose_name = _("scan tag")
        verbose_name_plural = _("scan tags")

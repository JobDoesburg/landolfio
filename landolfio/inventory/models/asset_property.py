from django.db import models
from django.utils.translation import gettext_lazy as _
from django.core.exceptions import ValidationError
from django.utils.text import slugify
import json


class AssetPropertyType(models.TextChoices):
    STRING = "string", _("String")
    NUMBER = "number", _("Number")
    DROPDOWN = "dropdown", _("Dropdown")


class AssetProperty(models.Model):
    """
    Defines a property that can be assigned to assets of a specific category.
    """
    category = models.ForeignKey(
        "Category",
        on_delete=models.CASCADE,
        related_name="properties",
        verbose_name=_("category"),
    )
    name = models.CharField(
        max_length=100,
        verbose_name=_("property name"),
        help_text=_("The name of this property (e.g., 'Color', 'Weight', 'Material')")
    )
    slug = models.SlugField(
        max_length=100,
        unique=True,
        blank=True,
        null=True,
        verbose_name=_("slug"),
        help_text=_("URL-friendly version with category prefix (e.g., 'electronics-color', 'furniture-weight')")
    )
    property_type = models.CharField(
        max_length=20,
        choices=AssetPropertyType.choices,
        default=AssetPropertyType.STRING,
        verbose_name=_("property type"),
    )
    unit = models.CharField(
        max_length=20,
        blank=True,
        verbose_name=_("unit"),
        help_text=_("Unit for numeric properties (e.g., 'kg', 'cm', 'V')")
    )
    dropdown_options = models.TextField(
        blank=True,
        verbose_name=_("dropdown options"),
        help_text=_("JSON array of options for dropdown properties (e.g., [\"Red\", \"Blue\", \"Green\"])")
    )
    order = models.PositiveIntegerField(
        default=0,
        verbose_name=_("display order"),
        help_text=_("Order in which properties are displayed")
    )

    class Meta:
        verbose_name = _("asset property")
        verbose_name_plural = _("asset properties")
        unique_together = [("category", "name")]
        ordering = ["category", "order", "name"]

    def __str__(self):
        return f"{self.category.name} - {self.name}"

    def clean(self):
        super().clean()
        
        # Validate dropdown options
        if self.property_type == AssetPropertyType.DROPDOWN:
            if not self.dropdown_options:
                raise ValidationError({
                    'dropdown_options': _('Dropdown options are required for dropdown properties')
                })
            try:
                options = json.loads(self.dropdown_options)
                if not isinstance(options, list) or not all(isinstance(opt, str) for opt in options):
                    raise ValidationError({
                        'dropdown_options': _('Dropdown options must be a JSON array of strings')
                    })
            except json.JSONDecodeError:
                raise ValidationError({
                    'dropdown_options': _('Invalid JSON format for dropdown options')
                })
        
        # Validate unit for numeric properties
        if self.property_type == AssetPropertyType.NUMBER and not self.unit:
            # Unit is optional for numeric properties, just a suggestion
            pass

    def get_dropdown_options(self):
        """Return parsed dropdown options as a list."""
        if self.property_type == AssetPropertyType.DROPDOWN and self.dropdown_options:
            try:
                return json.loads(self.dropdown_options)
            except json.JSONDecodeError:
                return []
        return []

    def _generate_slug(self):
        """Generate a category-prefixed slug from the property name."""
        if not self.category:
            raise ValidationError({'category': _('Category is required to generate slug')})
        
        category_slug = slugify(self.category.name_singular)
        property_slug = slugify(self.name)
        return f"{category_slug}-{property_slug}"
    
    def save(self, *args, **kwargs):
        # Auto-generate slug if not provided
        if not self.slug:
            self.slug = self._generate_slug()
        
        self.full_clean()
        super().save(*args, **kwargs)


class AssetPropertyValue(models.Model):
    """
    Stores the actual value of a property for a specific asset.
    """
    asset = models.ForeignKey(
        "Asset",
        on_delete=models.CASCADE,
        related_name="property_values",
        verbose_name=_("asset"),
    )
    property = models.ForeignKey(
        AssetProperty,
        on_delete=models.CASCADE,
        related_name="values",
        verbose_name=_("property"),
    )
    value = models.TextField(
        verbose_name=_("value"),
        help_text=_("The value of this property for this asset")
    )

    class Meta:
        verbose_name = _("asset property value")
        verbose_name_plural = _("asset property values")
        unique_together = [("asset", "property")]

    def __str__(self):
        return f"{self.asset.name} - {self.property.name}: {self.value}"

    def clean(self):
        super().clean()
        
        # Validate that the property belongs to the asset's category
        if self.asset.category != self.property.category:
            raise ValidationError({
                'property': _('Property must belong to the same category as the asset')
            })
        
        # Validate value based on property type
        if self.property.property_type == AssetPropertyType.NUMBER:
            try:
                float(self.value)
            except (ValueError, TypeError):
                raise ValidationError({
                    'value': _('Value must be a valid number for numeric properties')
                })
        
        elif self.property.property_type == AssetPropertyType.DROPDOWN:
            options = self.property.get_dropdown_options()
            if self.value not in options:
                raise ValidationError({
                    'value': _('Value must be one of the allowed dropdown options: {}').format(', '.join(options))
                })

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    def get_formatted_value(self):
        """Return the value formatted with unit if applicable."""
        if self.property.property_type == AssetPropertyType.NUMBER and self.property.unit:
            return f"{self.value} {self.property.unit}"
        return self.value
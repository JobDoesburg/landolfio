import logging
import uuid
from datetime import datetime

from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import PROTECT, Count
from django.urls import reverse
from django.utils.translation import gettext
from django.utils.translation import gettext_lazy as _

from inventory.moneybird import MoneybirdAssetService

logger = logging.getLogger(__name__)
from queryable_properties.managers import QueryablePropertiesManager
from queryable_properties.properties import (
    AggregateProperty,
    RelatedExistenceCheckProperty,
)

from inventory.models.category import Category, Size
from inventory.models.collection import Collection
from inventory.models.location import Location


class FilteredRelatedExistenceCheckProperty(RelatedExistenceCheckProperty):
    def __init__(self, check_property, filter=None, *args, **kwargs):
        super().__init__(check_property, *args, **kwargs)
        self.filter = filter

    def get_queryset(self, model):
        return super().get_queryset(model).filter(self.filter)


class AssetStates(models.TextChoices):
    UNKNOWN = "unknown", _("unknown")
    PLACEHOLDER = "placeholder", _("placeholder")
    TO_BE_DELIVERED = "to_be_delivered", _("to be delivered")
    UNDER_REVIEW = "under_review", _("under review")
    MAINTENANCE_IN_HOUSE = "maintenance_in_house", _("maintenance in house")
    MAINTENANCE_EXTERNAL = "maintenance_external", _("maintenance external")
    AVAILABLE = "available", _("available")
    ISSUED_UNPROCESSED = "issued_unprocessed", _("issued unprocessed")
    ISSUED_RENT = "issued_rent", _("issued rent")
    ISSUED_LOAN = "issued_loan", _("issued loan")
    AMORTIZED = "amortized", _("amortized")
    SOLD = "sold", _("sold")


class AccountingStates(models.TextChoices):
    UNKNOWN = "unknown", _("unknown")  # does not occur in the accounting system
    AVAILABLE = "available", _("available")  # purchased, not amortized, not sold
    AVAILABLE_OR_AMORTIZED = "available_or_amortized", _(
        "available or amortized"
    )  # amortized at purchase
    ISSUED_RENT = "issued_rent", _("issued rent")
    ISSUED_LOAN = "issued_loan", _("issued loan")
    AMORTIZED = "amortized", _("amortized")
    SOLD = "sold", _("sold")


def validate_uppercase(value):
    if not value.isupper():
        raise ValidationError(_("Name must be uppercase"))


class DisposalReasons(models.TextChoices):
    OUT_OF_USE = "out_of_use", _("out of use")
    DIVESTED = "divested", _("divested")


class Asset(models.Model):
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_("created at"))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_("updated at"))
    id = models.UUIDField(
        primary_key=True, editable=False, default=uuid.uuid4, verbose_name=_("id")
    )
    name = models.CharField(
        verbose_name=_("name"),
        null=False,
        blank=False,
        max_length=255,
        unique=True,
        # validators=[validate_slug, validate_uppercase],
    )
    category = models.ForeignKey(
        Category,
        null=True,
        blank=False,
        on_delete=PROTECT,
        verbose_name=_("category"),
    )
    size = models.ForeignKey(
        Size, null=True, blank=True, on_delete=PROTECT, verbose_name=_("size")
    )
    location = models.ForeignKey(
        Location,
        null=True,
        blank=True,
        on_delete=PROTECT,
        verbose_name=_("location"),
    )
    location_nr = models.PositiveSmallIntegerField(
        verbose_name=_("location nr"), null=True, blank=True
    )
    collection = models.ForeignKey(
        Collection, on_delete=models.CASCADE, verbose_name=_("collection")
    )

    listing_price = models.DecimalField(
        verbose_name=_("listing price"),
        null=True,
        blank=True,
        max_digits=10,
        decimal_places=2,
    )
    # DEPRECATED: Use current_status property which gets status from StatusChange model
    # This field is kept for backwards compatibility and as fallback when no StatusChanges exist
    local_status = models.CharField(
        max_length=40,
        choices=AssetStates.choices,
        verbose_name=_("local status"),
        default=AssetStates.UNKNOWN,
    )

    raw_data = models.JSONField(verbose_name=_("raw data"), null=True, blank=True)

    moneybird_asset_id = models.BigIntegerField(
        verbose_name=_("Moneybird asset ID"),
        null=True,
        blank=True,
        unique=True,
        help_text=_("ID of the corresponding asset in Moneybird"),
    )
    moneybird_data = models.JSONField(
        verbose_name=_("Moneybird data"),
        null=True,
        blank=True,
        help_text=_("Cached data from Moneybird API"),
    )
    start_date = models.DateField(
        verbose_name=_("start date"),
        null=True,
        blank=True,
        help_text=_("Date when the asset was put into service"),
    )
    is_margin_asset = models.BooleanField(
        verbose_name=_("is margin"),
        default=False,
        help_text=_(
            "From a tax perspective, is this property a used good to which the margin scheme applies (purchased from a consumer or purchased under the margin scheme)?"
        ),
    )
    purchase_value_asset = models.DecimalField(
        verbose_name=_("purchase value"),
        null=True,
        blank=True,
        max_digits=10,
        decimal_places=2,
        help_text=_("Purchase value of the asset"),
    )
    disposal = models.CharField(
        max_length=20,
        choices=DisposalReasons.choices,
        blank=True,
        null=True,
        verbose_name=_("disposal status"),
        help_text=_("Asset disposal reason from Moneybird data"),
    )
    current_value = models.DecimalField(
        verbose_name=_("current value"),
        null=True,
        blank=True,
        max_digits=10,
        decimal_places=2,
        help_text=_("Current value of the asset from Moneybird"),
    )

    attachment_count = AggregateProperty(Count("attachments"))

    @property
    def current_status(self):
        """Get the current status from the latest StatusChange with a non-null new_status."""
        if not hasattr(self, "_current_status_cache"):
            try:
                # Find the most recent status change that actually changed the status
                latest_change = (
                    self.status_changes.filter(new_status__isnull=False)
                    .order_by("-status_date", "-created_at")
                    .first()
                )
                self._current_status_cache = (
                    latest_change.new_status if latest_change else self.local_status
                )
            except:
                # Fallback to local_status if no status changes exist yet
                self._current_status_cache = self.local_status
        return self._current_status_cache

    @property
    def current_status_display(self):
        """Get the display name for the current status."""
        for choice_value, choice_display in AssetStates.choices:
            if choice_value == self.current_status:
                return choice_display
        return self.current_status

    @property
    def is_disposed(self):
        """Boolean property to check if asset has been disposed/amortized."""
        return bool(self.disposal)

    @property
    def disposal_reason_display(self):
        """Get human-readable disposal reason."""
        return self.get_disposal_display() if self.disposal else None

    @property
    def is_financially_unlinked(self):
        """Check if asset is financially unlinked based on sources in Moneybird data."""
        if not self.moneybird_data or not isinstance(self.moneybird_data, dict):
            return True

        sources = self.moneybird_data.get("sources", [])
        return not sources or len(sources) == 0

    @property
    def sources_count(self):
        """Get the number of source documents linked to this asset in Moneybird."""
        if not self.moneybird_data or not isinstance(self.moneybird_data, dict):
            return 0

        sources = self.moneybird_data.get("sources", [])
        return len(sources)

    @property
    def financial_status(self):
        """Get the financial status for badge display."""
        # Determine base status first
        base_status = None
        base_color = None

        # If there's a disposal, use disposal-based status
        if self.disposal:
            if self.disposal == "out_of_use":
                from inventory.models.status_type import StatusType

                try:
                    status_type = StatusType.objects.get(slug="out_of_use")
                    base_status = status_type.name
                    base_color = status_type.background_color
                except StatusType.DoesNotExist:
                    base_status = str(_("out of use"))
                    base_color = "dark"
            elif self.disposal == "divested":
                from inventory.models.status_type import StatusType

                try:
                    status_type = StatusType.objects.get(slug="divested")
                    base_status = status_type.name
                    base_color = status_type.background_color
                except StatusType.DoesNotExist:
                    base_status = str(_("divested"))
                    base_color = "secondary"
        else:
            # No disposal, check current value
            current_val = self.current_value or 0
            if current_val == 0:
                # Active depreciated (no margin suffix)
                base_status = str(_("active depreciated"))
                base_color = "success"
            else:
                # Active
                base_status = str(_("active"))
                base_color = "success"

        # Check for status mismatch with local status
        has_mismatch = False
        if self.moneybird_asset_id:  # Only check if financially linked
            current = self.current_status
            if current == "amortized" and self.disposal != "out_of_use":
                has_mismatch = True
            elif current == "sold" and self.disposal != "divested":
                has_mismatch = True
            elif self.disposal == "out_of_use" and current != "amortized":
                has_mismatch = True
            elif self.disposal == "divested" and current != "sold":
                has_mismatch = True

        # Append unlink icon if financially unlinked (no sources)
        if self.is_financially_unlinked:
            base_status += ' <i class="fa-solid fa-link-slash fa-xs"></i>'

        # Append warning symbol if there's a status mismatch
        if has_mismatch:
            base_status += ' <i class="fa-solid fa-triangle-exclamation fa-xs"></i>'

        return {"status": base_status, "color": base_color}

    @property
    def financial_status_display(self):
        """Get the display text for financial status."""
        return self.financial_status["status"]

    @property
    def financial_status_color(self):
        """Get the Bootstrap color class for financial status."""
        color = self.financial_status["color"]
        # Map custom colors to Bootstrap classes
        color_map = {
            "black": "dark",
            "green": "success",
            "yellow": "warning",
            "blue": "primary",
            "red": "danger",
            "grey": "secondary",
            "gray": "secondary",
        }
        return color_map.get(color, color)

    @property
    def has_status_warning(self):
        """Check if there's a status mismatch warning."""
        if not self.moneybird_asset_id:
            return False

        current = self.current_status
        if current == "amortized" and self.disposal != "out_of_use":
            return True
        elif current == "sold" and self.disposal != "divested":
            return True
        elif self.disposal == "out_of_use" and current != "amortized":
            return True
        elif self.disposal == "divested" and current != "sold":
            return True

        return False

    @property
    def status_warning_message(self):
        """Get the warning message for status mismatch."""
        if not self.moneybird_asset_id:
            return None

        if self.is_financially_unlinked:
            return gettext("Asset is financially unlinked")

        current = self.current_status
        if current == "amortized" and self.disposal != "out_of_use":
            return gettext(
                "Local status is amortized but financial disposal is not out of use"
            )
        elif current == "sold" and self.disposal != "divested":
            return gettext(
                "Local status is sold but financial disposal is not divested"
            )
        elif self.disposal == "out_of_use" and current != "amortized":
            return gettext(
                "Financial disposal is out of use but local status is not amortized"
            )
        elif self.disposal == "divested" and current != "sold":
            return gettext(
                "Financial disposal is divested but local status is not sold"
            )

        return None

    objects = QueryablePropertiesManager()

    def __str__(self):
        category_name = self.category.name_singular if self.category else "Asset"
        size_str = f" ({self.size})" if self.size else ""
        return f"{category_name} {self.name}{size_str}"

    def save(self, *args, **kwargs):
        """Override save to ensure non-commerce assets are always margin assets."""
        if self.collection and not self.collection.commerce:
            self.is_margin_asset = True
        super().save(*args, **kwargs)

    def get_asset_ledger_account_id(self):
        """Get the appropriate ledger account ID based on margin status."""
        if self.is_margin_asset:
            return settings.MONEYBIRD_MARGIN_ASSETS_LEDGER_ACCOUNT_ID
        else:
            return settings.MONEYBIRD_NOT_MARGIN_ASSETS_LEDGER_ACCOUNT_ID

    def refresh_from_moneybird(self):
        """Refresh asset data from Moneybird API if moneybird_asset_id is set."""
        if not self.moneybird_asset_id:
            return None

        mb = MoneybirdAssetService()
        try:
            moneybird_data = mb.get_asset_financial_info(self.moneybird_asset_id)
            return self._refresh_from_moneybird(moneybird_data)
        except Exception as e:
            # Check if it's a 404 error (asset doesn't exist on Moneybird)
            if "404" in str(e) or "Not Found" in str(e):
                logger.warning(
                    f"Asset {self.id} (Moneybird ID: {self.moneybird_asset_id}) not found on Moneybird, unlinking asset and clearing Moneybird data"
                )
                # Clear all Moneybird-related data since the asset no longer exists
                self.moneybird_asset_id = None
                self.moneybird_data = None
                self.disposal = None
                self.current_value = None
                # Note: We keep purchase_value_asset and start_date as they're local business data
                self.save(
                    update_fields=[
                        "moneybird_asset_id",
                        "moneybird_data",
                        "disposal",
                        "current_value",
                    ]
                )
                return None
            else:
                logger.error(
                    f"Failed to refresh Moneybird data for asset {self.id}: {e}"
                )
                return None

    def _refresh_from_moneybird(self, moneybird_data=None):
        """Refresh asset data with Moneybird API data."""
        self.moneybird_data = moneybird_data

        if "purchase_date" in moneybird_data:
            self.start_date = datetime.strptime(
                moneybird_data["purchase_date"], "%Y-%m-%d"
            ).date()

        if "purchase_value" in moneybird_data:
            self.purchase_value_asset = moneybird_data["purchase_value"]

        if "current_value" in moneybird_data:
            self.current_value = moneybird_data["current_value"]

        if "ledger_account_id" in moneybird_data:
            margin_account = settings.MONEYBIRD_MARGIN_ASSETS_LEDGER_ACCOUNT_ID
            if margin_account:
                self.is_margin_asset = str(moneybird_data["ledger_account_id"]) == str(
                    margin_account
                )

        # Check disposal data to set the disposal reason
        if "disposal" in moneybird_data and moneybird_data["disposal"]:
            disposal = moneybird_data["disposal"]
            disposal_reason = disposal.get("reason")
            # Map Moneybird disposal reasons to our choices
            if disposal_reason in [choice[0] for choice in DisposalReasons.choices]:
                self.disposal = disposal_reason
            else:
                # If unknown reason, default to out_of_use
                self.disposal = DisposalReasons.OUT_OF_USE
        else:
            # No disposal data means asset is still active
            self.disposal = None

        self.save(
            update_fields=[
                "moneybird_data",
                "start_date",
                "purchase_value_asset",
                "is_margin_asset",
                "disposal",
                "current_value",
            ]
        )
        return moneybird_data

    def create_on_moneybird(self):
        """Create a new asset on Moneybird and store the returned asset ID."""

        if not self.collection.commerce:
            raise ValueError(
                "Only assets in commercial collections can be pushed to Moneybird"
            )

        if self.moneybird_asset_id:
            raise ValueError("Asset already exists on Moneybird")

        if not self.start_date:
            raise ValueError("Asset must have a start_date to push to Moneybird")

        if not self.purchase_value_asset:
            raise ValueError("Asset must have a purchase_value to push to Moneybird")

        ledger_account_id = self.get_asset_ledger_account_id()
        if not ledger_account_id:
            raise ValueError("Cannot determine ledger account ID for asset")

        mb = MoneybirdAssetService()
        try:
            # Use asset name as Moneybird asset name
            asset_name = str(self)

            # Convert start_date to string format
            start_date_str = self.start_date.strftime("%Y-%m-%d")

            moneybird_data = mb.create_asset(
                name=asset_name,
                ledger_account_id=int(ledger_account_id),
                purchase_value=float(self.purchase_value_asset),
                start_date=start_date_str,
            )

            # Store the Moneybird asset ID and data
            self.moneybird_asset_id = moneybird_data["id"]
            self.moneybird_data = moneybird_data
            self.save(update_fields=["moneybird_asset_id", "moneybird_data"])

            return moneybird_data
        except Exception as e:
            logger.error(f"Failed to push asset {self.id} to Moneybird: {e}")
            raise

    def delete_from_moneybird(self):
        """Delete the asset from Moneybird."""
        if not self.moneybird_asset_id:
            raise ValueError("Asset is not linked to Moneybird.")

        mb = MoneybirdAssetService()
        try:
            mb.delete_asset(self.moneybird_asset_id)

            # Clear the Moneybird data from local asset
            self.moneybird_asset_id = None
            self.moneybird_data = None
            self.save(update_fields=["moneybird_asset_id", "moneybird_data"])

            return True
        except Exception as e:
            logger.error(f"Failed to delete asset {self.id} from Moneybird: {e}")
            raise

    def update_on_moneybird(self):
        """Update the asset on Moneybird with current local data."""
        if not self.moneybird_asset_id:
            raise ValueError("Asset is not linked to Moneybird.")

        mb = MoneybirdAssetService()
        try:
            # Prepare update data
            asset_name = str(self)
            ledger_account_id = self.get_asset_ledger_account_id()

            # Convert start_date to string format if available
            start_date_str = None
            if self.start_date:
                start_date_str = self.start_date.strftime("%Y-%m-%d")

            # Update the asset on Moneybird
            moneybird_data = mb.update_asset(
                asset_id=self.moneybird_asset_id,
                name=asset_name,
                ledger_account_id=ledger_account_id if ledger_account_id else None,
                purchase_date=start_date_str,
                purchase_value=(
                    float(self.purchase_value_asset)
                    if self.purchase_value_asset
                    else None
                ),
            )

            # Update local moneybird_data with the response
            self.moneybird_data = moneybird_data
            self.save(update_fields=["moneybird_data"])

            return moneybird_data
        except Exception as e:
            logger.error(f"Failed to update asset {self.id} on Moneybird: {e}")
            raise

    def dispose_on_moneybird(self, disposal_date, disposal_reason):
        """Dispose the asset on Moneybird with given date and reason."""
        if not self.moneybird_asset_id:
            raise ValueError("Asset is not linked to Moneybird.")

        mb = MoneybirdAssetService()
        try:
            # Format the date
            date_str = (
                disposal_date.strftime("%Y-%m-%d")
                if hasattr(disposal_date, "strftime")
                else disposal_date
            )

            # First check the current asset value from Moneybird
            current_asset_data = mb.get_asset_financial_info(self.moneybird_asset_id)

            # Check if asset has zero value before allowing disposal
            current_value = current_asset_data.get("current_value", 0)
            if current_value != "0.0":
                raise ValueError(
                    f"Asset cannot be disposed as it still has a value of {current_value}. The asset must be fully depreciated first."
                )

            # Dispose the asset on Moneybird
            logger.info(f"Disposing asset {self.id} on Moneybird")
            disposal_data = mb.dispose_asset(
                asset_id=self.moneybird_asset_id,
                disposal_date=date_str,
                disposal_reason=disposal_reason,
            )

            # Update local asset data
            self.disposal = disposal_reason
            self.moneybird_data = disposal_data
            self.save(update_fields=["disposal", "moneybird_data"])

            return disposal_data
        except Exception as e:
            logger.error(f"Failed to dispose asset {self.id} on Moneybird: {e}")
            raise

    def fully_depreciate_on_moneybird(
        self, depreciation_date, description="Full depreciation"
    ):
        """Fully depreciate the asset on Moneybird. This will go to the "Afschrijvingskosten" account and create an "out-of-use" disposal."""
        if not self.moneybird_asset_id:
            raise ValueError("Asset is not linked to Moneybird.")

        mb = MoneybirdAssetService()
        try:
            # Format the date
            date_str = (
                depreciation_date.strftime("%Y-%m-%d")
                if hasattr(depreciation_date, "strftime")
                else depreciation_date
            )

            logger.info(f"Fully depreciating asset {self.id} on Moneybird")
            depreciation_data = mb.fully_depreciate_asset(
                asset_id=self.moneybird_asset_id,
                depreciation_date=date_str,
                description=description,
            )

            # Update local asset data
            self.moneybird_data = depreciation_data
            self.save(update_fields=["moneybird_data"])

            return depreciation_data
        except Exception as e:
            logger.error(
                f"Failed to fully depreciate asset {self.id} on Moneybird: {e}"
            )
            raise

    def create_manual_value_change_on_moneybird(
        self, change_date, amount, description, externally_booked=False
    ):
        """Create a manual value change for the asset on Moneybird. This will go to the "Afschrijvingskosten" account."""
        if not self.moneybird_asset_id:
            raise ValueError("Asset is not linked to Moneybird.")

        mb = MoneybirdAssetService()
        try:
            # Format the date
            date_str = (
                change_date.strftime("%Y-%m-%d")
                if hasattr(change_date, "strftime")
                else change_date
            )

            value_change_data = mb.create_manual_value_change(
                asset_id=self.moneybird_asset_id,
                change_date=date_str,
                amount=amount,
                description=description,
                externally_booked=externally_booked,
            )

            # Update local asset data
            self.moneybird_data = value_change_data
            self.save(update_fields=["moneybird_data"])

            return value_change_data
        except Exception as e:
            logger.error(
                f"Failed to create manual value change for asset {self.id} on Moneybird: {e}"
            )
            raise

    def create_arbitrary_value_change_on_moneybird(
        self, change_date, amount, description, externally_booked=False
    ):
        """Create an arbitrary value change for the asset on Moneybird. This will go to the "Afschrijvingskosten" account."""
        if not self.moneybird_asset_id:
            raise ValueError("Asset is not linked to Moneybird.")

        mb = MoneybirdAssetService()
        try:
            # Format the date
            date_str = (
                change_date.strftime("%Y-%m-%d")
                if hasattr(change_date, "strftime")
                else change_date
            )

            value_change_data = mb.create_arbitrary_value_change(
                asset_id=self.moneybird_asset_id,
                change_date=date_str,
                amount=amount,
                description=description,
                externally_booked=externally_booked,
            )

            # Update local asset data
            self.moneybird_data = value_change_data
            self.save(update_fields=["moneybird_data"])

            return value_change_data
        except Exception as e:
            logger.error(
                f"Failed to create arbitrary value change for asset {self.id} on Moneybird: {e}"
            )
            raise

    def create_divestment_value_change_on_moneybird(self, change_date):
        """Create a divestment value change for the asset on Moneybird. This will go to the "Boekresultaat" account and create a "divestment" disposal."""
        if not self.moneybird_asset_id:
            raise ValueError("Asset is not linked to Moneybird.")

        mb = MoneybirdAssetService()
        try:
            # Format the date
            date_str = (
                change_date.strftime("%Y-%m-%d")
                if hasattr(change_date, "strftime")
                else change_date
            )

            value_change_data = mb.create_divestment_value_change(
                asset_id=self.moneybird_asset_id, change_date=date_str
            )

            # Divestment automatically creates a disposal, so update disposal status
            self.disposal = "divested"
            self.moneybird_data = value_change_data
            self.save(update_fields=["disposal", "moneybird_data"])

            return value_change_data
        except Exception as e:
            logger.error(
                f"Failed to create divestment value change for asset {self.id} on Moneybird: {e}"
            )
            raise

    def create_status_change(self, new_status, status_date, comments=""):
        """Create a new status change for this asset."""
        from inventory.models.status_change import StatusChange

        status_change = StatusChange.objects.create(
            asset=self,
            new_status=new_status,
            status_date=status_date,
            comments=comments,
        )

        # Clear the cached current status
        if hasattr(self, "_current_status_cache"):
            del self._current_status_cache

        return status_change

    def get_absolute_url(self):
        return reverse("admin:inventory_asset_view", args=[self.id])

    @property
    def moneybird_asset_url(self):
        """Get the Moneybird asset URL if asset ID is available."""
        if self.moneybird_asset_id:
            administration_id = getattr(settings, "MONEYBIRD_ADMINISTRATION_ID", None)
            if administration_id:
                return f"https://moneybird.com/{administration_id}/assets/{self.moneybird_asset_id}"
        return None

    @property
    def moneybird_asset_name(self):
        """Get the asset name from Moneybird data."""
        if self.moneybird_data and isinstance(self.moneybird_data, dict):
            return self.moneybird_data.get("name", self.moneybird_asset_id)
        return self.moneybird_asset_id

    class Meta:
        ordering = ["-created_at", "name"]
        verbose_name = _("asset")
        verbose_name_plural = _("assets")

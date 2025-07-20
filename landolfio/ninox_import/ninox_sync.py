import logging

import bleach
import requests
from django.core.files.base import ContentFile
from django.utils.dateparse import parse_datetime
from django.utils.text import slugify
from django.utils.timezone import make_aware
from requests import HTTPError
from requests.auth import AuthBase

from django.conf import settings

from inventory.models.asset import Asset
from inventory.models.attachment import Attachment
from inventory.models.category import Category, Size
from inventory.models.collection import Collection
from inventory.models.location import LocationGroup, Location
from inventory.models.remarks import Remark
from inventory.models.asset import AssetStates


class TokenAuthentication(AuthBase):
    def __init__(self, auth_token: str = ""):
        self.auth_token = auth_token

    def __call__(self, r):
        r.headers.update(
            {
                "Authorization": "Bearer %s" % self.auth_token,
            }
        )
        return r


def get_or_create_location(group_name, location_name):
    location_group, _ = LocationGroup.objects.get_or_create(name=group_name)
    return Location.objects.get_or_create(
        name=location_name, location_group=location_group
    )


class NinoxImporter:
    _logger = logging.getLogger("django.ninox")

    api_version = "v1"
    api_token = settings.NINOX_API_TOKEN
    team_id = settings.NINOX_TEAM_ID
    database_id = settings.NINOX_DATABASE_ID

    ninox_table_to_asset_category = {
        "Cello's": Category.objects.get_or_create(
            name="Cello's", name_singular="Cello"
        ),
        "Cellostokken": Category.objects.get_or_create(
            name="Cellostokken", name_singular="Cellostok"
        ),
        "Violen": Category.objects.get_or_create(name="Violen", name_singular="Viool"),
        "Vioolstokken": Category.objects.get_or_create(
            name="Vioolstokken", name_singular="Vioolstok"
        ),
        "Altviolen": Category.objects.get_or_create(
            name="Altviolen", name_singular="Altviool"
        ),
        "Altvioolstokken": Category.objects.get_or_create(
            name="Altvioolstokken", name_singular="Altvioolstok"
        ),
        "Contrabassen": Category.objects.get_or_create(
            name="Contrabassen", name_singular="Contrabas"
        ),
        "Contrabasstokken": Category.objects.get_or_create(
            name="Contrabasstokken", name_singular="Contrabasstok"
        ),
        "Gamba's": Category.objects.get_or_create(
            name="Gamba's", name_singular="Gamba"
        ),
        "Gambastokken": Category.objects.get_or_create(
            name="Gambastokken", name_singular="Gambastok"
        ),
    }

    ninox_status_to_asset_status = {
        "In huis beschikbaar - boven": AssetStates.AVAILABLE,
        "In huis beschikbaar - beneden": AssetStates.AVAILABLE,
        "Uitgeleend": AssetStates.ISSUED_LOAN,
        "In afwachting bij docent": AssetStates.ISSUED_UNPROCESSED,
        "Verhuurd": AssetStates.ISSUED_RENT,
        "Verkocht": AssetStates.SOLD,
        "Reparatie - in huis": AssetStates.MAINTENANCE_IN_HOUSE,
        "Reparatie - extern": AssetStates.MAINTENANCE_EXTERNAL,
        "Verdwenen": AssetStates.UNKNOWN,
        "Afgeschreven": AssetStates.AMORTIZED,
        "Nog niet geleverd": AssetStates.TO_BE_DELIVERED,
    }

    ninox_collection_to_collection = {
        "Zakelijk": Collection.objects.get_or_create(name="Zakelijk", commerce=True)[0],
        "Prive": Collection.objects.get_or_create(name="Prive", commerce=False)[0],
        "Consignatie": Collection.objects.get_or_create(
            name="Consignatie", commerce=False
        )[0],
        "Zakelijk (S)": Collection.objects.get_or_create(
            name="Schreeven", commerce=True
        )[0],
        "Algemene registratie": Collection.objects.get_or_create(
            name="Overig", commerce=False
        )[0],
    }

    ninox_category_to_category = {
        "Cello": Category.objects.get_or_create(name="Cello's", name_singular="Cello"),
        "Cellostok": Category.objects.get_or_create(
            name="Cellostokken", name_singular="Cellostok"
        ),
        "Viool": Category.objects.get_or_create(name="Violen", name_singular="Viool"),
        "Vioolstok": Category.objects.get_or_create(
            name="Vioolstokken", name_singular="Vioolstok"
        ),
        "Altviool": Category.objects.get_or_create(
            name="Altviolen", name_singular="Altviool"
        ),
        "Altvioolstok": Category.objects.get_or_create(
            name="Altvioolstokken", name_singular="Altvioolstok"
        ),
        "Contrabas": Category.objects.get_or_create(
            name="Contrabassen", name_singular="Contrabas"
        ),
        "Contrabasstok": Category.objects.get_or_create(
            name="Contrabasstokken", name_singular="Contrabasstok"
        ),
        "Gamba": Category.objects.get_or_create(name="Gamba's", name_singular="Gamba"),
        "Gambastok": Category.objects.get_or_create(
            name="Gambastokken", name_singular="Gambastok"
        ),
    }

    ninox_location_to_asset_location = {
        "Boven": get_or_create_location("Opslag", "-"),
        "Boven - Keuken": get_or_create_location("Boven", "Keuken"),
        "Boven - Vleugelkamer": get_or_create_location("Boven", "Vleugelkamer"),
        "Boven - Hal": get_or_create_location("Boven", "Hal"),
        "Boven - Hal trap": get_or_create_location("Boven", "Hal trap"),
        "Boven - Studeerkamer": get_or_create_location("Boven", "Studeerkamer"),
        "Boven - Kleine kamer": get_or_create_location("Boven", "Kleine kamer"),
        "Boven - Badkamer": get_or_create_location("Boven", "Badkamer"),
        "Beneden - Schouw": get_or_create_location("Beneden", "Schouw"),
        "Beneden - Muur schouw": get_or_create_location("Beneden", "Muur schouw"),
        "Beneden - Muur schouw 1": get_or_create_location("Beneden", "Muur schouw"),
        "Beneden - Muur schouw 2": get_or_create_location("Beneden", "Muur schouw"),
        "Beneden - Muur schouw 3": get_or_create_location("Beneden", "Muur schouw"),
        "Beneden - Muur schouw 4": get_or_create_location("Beneden", "Muur schouw"),
        "Muur schouw 1": get_or_create_location("Beneden", "Muur schouw"),
        "Muur schouw 2": get_or_create_location("Beneden", "Muur schouw"),
        "Muur schouw 3": get_or_create_location("Beneden", "Muur schouw"),
        "Muur schouw 4": get_or_create_location("Beneden", "Muur schouw"),
        "Beneden - Kast 1/1": get_or_create_location("Beneden", "Kast 1/1"),
        "Beneden - Kast 1/2": get_or_create_location("Beneden", "Kast 1/2"),
        "Beneden - Kast 1/3": get_or_create_location("Beneden", "Kast 1/3"),
        "Beneden - Kast 2/1": get_or_create_location("Beneden", "Kast 2/1"),
        "Beneden - Kast 2/2": get_or_create_location("Beneden", "Kast 2/2"),
        "Beneden - Kast 2/3": get_or_create_location("Beneden", "Kast 2/3"),
        "Beneden - Kast 2/4": get_or_create_location("Beneden", "Kast 2/4"),
        "Beneden - Kast 2/5": get_or_create_location("Beneden", "Kast 2/5"),
        "Beneden - Kast 0/1": get_or_create_location("Beneden", "Kast 0/1"),
        "Beneden - Kast 0/2": get_or_create_location("Beneden", "Kast 0/2"),
        "Beneden - Kast 0/3": get_or_create_location("Beneden", "Kast 0/3"),
        "Beneden - Kast 0/4": get_or_create_location("Beneden", "Kast 0/4"),
        "Beneden - Kast 0/5": get_or_create_location("Beneden", "Kast 0/5"),
        "Beneden - Kast 0/6": get_or_create_location("Beneden", "Kast 0/6"),
        "Boven - Keuken kast": get_or_create_location("Boven", "Keuken - kast"),
        "Boven - Keuken kast links": get_or_create_location(
            "Boven", "Keuken - kast links"
        ),
        "Boven - Keuken links boven": get_or_create_location(
            "Boven", "Keuken - kast links"
        ),
        "Boven - Keuken links onder": get_or_create_location(
            "Boven", "Keuken - kast links"
        ),
        "Boven - Keuken rechts boven": get_or_create_location(
            "Boven", "Keuken - kast rechts"
        ),
        "Boven - Keuken rechts onder": get_or_create_location(
            "Boven", "Keuken - kast rechts"
        ),
    }

    def get(self, url, stream=False):
        try:
            self._logger.info(f"Sending request: {url}")
            response = requests.get(
                url, auth=TokenAuthentication(self.api_token), stream=stream
            )
            response.raise_for_status()
            self._logger.info(f"Got response: {response}")
        except HTTPError as http_err:
            self._logger.error(f"HTTP error occurred: {http_err}")
        except Exception as err:
            self._logger.error(f"Other error occurred: {err}")
        else:
            if stream:
                return response

            try:
                return response.json()
            except ValueError:
                return response

    def get_ninox_endpoint_url(
        self, table_id=None, record_id=None, fetch_files=False, filename=None
    ):
        url = f"https://api.ninox.com/{self.api_version}/teams"
        if self.team_id:
            url = f"{url}/{self.team_id}/databases"
        if self.database_id:
            url = f"{url}/{self.database_id}/tables"
        if table_id:
            url = f"{url}/{table_id}/records"
        if record_id:
            url = f"{url}/{record_id}"
            if fetch_files or filename:
                url = f"{url}/files"
        if filename:
            url = f"{url}/{filename}"

        if not record_id and not filename:
            return f"{url}?perPage=2000"

        return url

    def create_asset(self, record, category):
        try:
            asset_number = record["fields"]["Nummer"]
        except KeyError:
            self._logger.warning(
                f"Found a {category} asset without number, skipping: {record}"
            )
            return None, None, None

        try:
            status = self.ninox_status_to_asset_status[record["fields"]["Status"]]
        except KeyError:
            self._logger.warning(
                f"Could not match status for {category} asset {asset_number}"
            )
            status = AssetStates.UNKNOWN

        already_existing_in_different_category = (
            Asset.objects.exclude(category=category).filter(name=asset_number).exists()
        )
        if already_existing_in_different_category:
            new_asset_number = slugify(f"{asset_number}-{category}")
            self._logger.warning(
                f"Asset {asset_number} already exists in a different category, changing the number to {new_asset_number}"
            )
            asset_number = new_asset_number

        try:
            collection = self.ninox_collection_to_collection[
                record["fields"]["Collectie"]
            ]
        except KeyError:
            self._logger.warning(f"Could not match collection asset {asset_number}")
            collection = self.ninox_collection_to_collection["Zakelijk"]

        asset, created = Asset.objects.get_or_create(
            name=asset_number,
            category=category,
            collection=collection,
        )

        if created:
            self._logger.warning(f"Created {asset}!")
        else:
            self._logger.warning(f"Already found {asset}!")

        return asset, created, status

    def update_asset_details(self, asset, record):
        try:
            size, _ = Size.objects.get_or_create(name=record["fields"]["Maat"])
            if not asset.category in size.categories.all():
                size.categories.add(asset.category)
        except KeyError:
            size = None

        try:
            collection = self.ninox_collection_to_collection[
                record["fields"]["Collectie"]
            ]
        except KeyError:
            self._logger.warning(f"Could not match collection for {asset}")
            collection = self.ninox_collection_to_collection["Zakelijk"]

        if "Locatie" in record["fields"]:
            try:
                location, _ = self.ninox_location_to_asset_location[
                    record["fields"]["Locatie"]
                ]
            except KeyError:
                self._logger.warning(f"Could not match location for {asset}")
                location = None
        else:
            location = None

        try:
            listing_price = record["fields"]["Waarde"]
        except KeyError:
            listing_price = None

        if "Status" in record["fields"]:
            try:
                status = self.ninox_status_to_asset_status[record["fields"]["Status"]]
            except KeyError:
                self._logger.info(f"Could not match status for {asset}")
                status = AssetStates.UNKNOWN
        else:
            status = AssetStates.UNKNOWN

        asset.size = size
        asset.listing_price = listing_price
        asset.location = location
        asset.local_status = status
        asset.collection = collection

        try:
            remarks = record["fields"]["Notities"]
            remarks = bleach.clean(remarks, tags=[], attributes={}, strip=True)
            Remark.objects.get_or_create(asset=asset, remark=remarks)
        except KeyError:
            pass

        asset.raw_data = record
        if (
            "createdAt" in record.keys()
            and record["createdAt"]
            and record["createdAt"] != ""
        ):
            asset.created_at = make_aware(parse_datetime(record["createdAt"]))
        elif (
            "updatedAt" in record.keys()
            and record["updatedAt"]
            and record["updatedAt"] != ""
        ):
            asset.created_at = make_aware(parse_datetime(record["updatedAt"]))

        asset.save()

    def update_asset_media(self, asset, record, table_id):
        record_attachments = self.get(
            self.get_ninox_endpoint_url(
                table_id=table_id, record_id=record["id"], fetch_files=True
            )
        )
        for attachment in record_attachments:
            filename = attachment["name"]
            filename_saved = filename.replace(" ", "_")
            if Attachment.objects.filter(
                asset=asset, attachment__endswith=filename_saved
            ).exists():
                self._logger.info(
                    f"File {filename_saved} for {asset} was already saved, skipping."
                )
                return

            try:
                file = self.get(
                    self.get_ninox_endpoint_url(
                        table_id=table_id, record_id=record["id"], filename=filename
                    ),
                    stream=True,
                )
                self._logger.info(f"Saving file {filename_saved} for {asset}.")

                if file:
                    attachment = Attachment(asset=asset)
                    attachment.attachment.save(
                        filename_saved, ContentFile(file.content), save=True
                    )
            except Exception as err:
                self._logger.warning(f"Some error occurred: {err}")

    def sync_ninox_record(self, record, category, table_id, with_media=True):
        asset, created, status = self.create_asset(record, category)

        if asset:
            self.update_asset_details(asset, record)
            if with_media:
                self.update_asset_media(asset, record, table_id)

    def sync_instrument_registrations(self, record, table_id, with_media=True):
        try:
            nummer = record["fields"]["Nummer"]
        except KeyError:
            logging.warning(f"Found an instrument without number, skipping: {record}")
            return
        try:
            collection = self.ninox_collection_to_collection[
                record["fields"]["Soort registratie"]
            ]
        except KeyError:
            collection = self.ninox_collection_to_collection["Algemene registratie"]

        try:
            size, _ = Size.objects.get_or_create(name=record["fields"]["Maat"])
        except KeyError:
            size = None

        try:
            category, _ = self.ninox_category_to_category[record["fields"]["Type"]]
        except KeyError:
            logging.warning(
                f"Could not match category for instrument {record['fields']['Nummer']}"
            )
            return

        try:
            listing_price = record["fields"]["Min. verkoopprijs"]
        except KeyError:
            listing_price = None

        asset, _ = Asset.objects.update_or_create(
            name=nummer,
            category=category,
            defaults={
                "collection": collection,
                "size": size,
                "listing_price": listing_price,
            },
        )

        asset.raw_data = record
        if (
            "createdAt" in record.keys()
            and record["createdAt"]
            and record["createdAt"] != ""
        ):
            asset.created_at = make_aware(parse_datetime(record["createdAt"]))
        elif (
            "updatedAt" in record.keys()
            and record["updatedAt"]
            and record["updatedAt"] != ""
        ):
            asset.created_at = make_aware(parse_datetime(record["updatedAt"]))
        asset.save()

        try:
            remarks = record["fields"]["Notities"]
            remarks = bleach.clean(remarks, tags=[], attributes={}, strip=True)
            Remark.objects.get_or_create(asset=asset, remark=remarks)
        except KeyError:
            pass

        if with_media:
            self.update_asset_media(asset, record, table_id)

    def full_sync(self, with_media=True, with_instrument_registrations=True):
        tables = self.get(self.get_ninox_endpoint_url())
        for table in tables:
            if not table["name"] in self.ninox_table_to_asset_category:
                if (
                    table["name"] == "Instrumentenregistraties"
                    and with_instrument_registrations
                ):
                    records = self.get(
                        self.get_ninox_endpoint_url(table_id=table["id"])
                    )
                    for record in records:
                        self.sync_instrument_registrations(
                            record, table["id"], with_media
                        )
                continue

            category, _ = self.ninox_table_to_asset_category[table["name"]]
            records = self.get(self.get_ninox_endpoint_url(table_id=table["id"]))
            for record in records:
                self.sync_ninox_record(record, category, table["id"], with_media)

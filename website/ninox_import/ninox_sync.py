import logging

import bleach
import requests
from django.core.exceptions import ValidationError
from django.core.files.base import ContentFile
from django.db import IntegrityError
from requests import HTTPError
from requests.auth import AuthBase

from django.conf import settings
from django.utils import timezone

from inventory.models import (
    AssetLocationGroup,
    AssetLocation,
    AssetCategory,
    Asset,
    AssetSize,
    AssetStates,
    Collection,
)


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
    location_group, _ = AssetLocationGroup.objects.get_or_create(name=group_name)
    return AssetLocation.objects.get_or_create(
        name=location_name, location_group=location_group
    )


class NinoxImporter:
    _logger = logging.getLogger("django.ninox")

    api_version = "v1"
    api_token = settings.NINOX_API_TOKEN
    team_id = settings.NINOX_TEAM_ID
    database_id = settings.NINOX_DATABASE_ID

    ninox_table_to_asset_category = {
        "Altviolen": AssetCategory.objects.get_or_create(
            name="Altviolen", name_singular="Altviool"
        ),
        "Altvioolstokken": AssetCategory.objects.get_or_create(
            name="Altvioolstokken", name_singular="Altvioolstok"
        ),
        "Cello's": AssetCategory.objects.get_or_create(
            name="Cello's", name_singular="Cello"
        ),
        "Cellostokken": AssetCategory.objects.get_or_create(
            name="Cellostokken", name_singular="Cellostok"
        ),
        "Violen": AssetCategory.objects.get_or_create(
            name="Violen", name_singular="Viool"
        ),
        "Vioolstokken": AssetCategory.objects.get_or_create(
            name="Vioolstokken", name_singular="Vioolstok"
        ),
        "Contrabassen": AssetCategory.objects.get_or_create(
            name="Contrabassen", name_singular="Contrabas"
        ),
        "Contrabassstokken": AssetCategory.objects.get_or_create(
            name="Contrabassstokken", name_singular="Contrabassstok"
        ),
        "Gamba's": AssetCategory.objects.get_or_create(
            name="Gamba's", name_singular="Gamba"
        ),
        "Gambastokken": AssetCategory.objects.get_or_create(
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

    ninox_location_to_asset_location = {
        "Boven - Keuken": get_or_create_location("Boven", "Keuken"),
        "Boven - Vleugelkamer": get_or_create_location("Boven", "Vleugelkamer"),
        "Boven - Hal": get_or_create_location("Boven", "Hal"),
        "Boven - Studeerkamer": get_or_create_location("Boven", "Studeerkamer"),
        "Beneden - Schouw": get_or_create_location("Beneden", "Schouw"),
        "Beneden - Stokkentafel": get_or_create_location("Beneden", "Stokkentafel"),
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
            print(f"HTTP error occurred: {http_err}")
        except Exception as err:
            print(f"Other error occurred: {err}")
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
            url = f"{url}/{table_id}/records?perPage=500"
        if record_id:
            url = f"{url}/{record_id}"
            if fetch_files or filename:
                url = f"{url}/files"
        if filename:
            url = f"{url}/{filename}"

        return url

    def create_asset(self, record, category):
        try:
            asset_number = record["fields"]["Nummer"]
        except KeyError:
            self._logger.error(
                f"Found a {category} asset without number, skipping: {record}"
            )
            return None, None, None

        try:
            status = self.ninox_status_to_asset_status[record["fields"]["Status"]]
        except KeyError:
            self._logger.error(
                f"Could not match status for {category} asset {asset_number}, skipping: {record}"
            )
            return None, None, None

        try:
            asset, created = Asset.objects.get_or_create(
                id=asset_number,
                category=category,
                collection=Collection.objects.filter(commerce=True).first(),
            )
        except (IntegrityError, ValidationError):
            self._logger.error(
                f"Could not synchronize {category} {asset_number}, does it have a valid (globally unique and a Unicode-slug) asset number?"
            )
            return None, None, None

        if created:
            self._logger.info(f"Created {asset}!")
        else:
            self._logger.info(f"Already found {asset}!")

        return asset, created, status

    def update_asset_details(self, asset, record):
        try:
            size, _ = AssetSize.objects.get_or_create(name=record["fields"]["Maat"])
            if not asset.category in size.categories.all():
                size.categories.add(asset.category)
        except KeyError:
            size = None

        try:
            location, _ = self.ninox_location_to_asset_location[
                record["fields"]["Locatie"]
            ]
        except KeyError:
            self._logger.error(
                f"Could not match location for {asset.category} asset {asset.id}"
            )
            location = None

        try:
            retail_value = record["fields"]["Waarde"]
        except KeyError:
            retail_value = None

        try:
            status = self.ninox_status_to_asset_status[record["fields"]["Status"]][0]
        except KeyError:
            self._logger.error(
                f"Could not match status for {asset.category} asset {asset.id}"
            )
            status = None

        asset.size = size
        asset.retail_value = retail_value
        asset.location = location
        asset.local_status = status

        try:
            remarks = record["fields"]["Notities"]
            remarks = bleach.clean(remarks, tags=[], attributes={}, strip=True)
            asset.remarks = remarks
        except KeyError:
            pass

        # TODO collectie
        # TODO detail velden
        asset.save()

    # def update_asset_media(self, asset, record, table_id):
    #     record_attachments = self.get(
    #         self.get_ninox_endpoint_url(table_id=table_id, record_id=record["id"], fetch_files=True)
    #     )
    #     initial_media_set = None
    #     for attachment in record_attachments:
    #         filename = attachment["name"]
    #         if MediaItem.objects.filter(set__asset=asset, media__endswith=filename):  # TODO better match
    #             self._logger.info(f"File {filename} for {asset} was already saved, skipping.")
    #             return
    #
    #         if not initial_media_set:
    #             initial_media_set = MediaSet.objects.filter(asset=asset).first()
    #             if not initial_media_set:
    #                 initial_media_set = MediaSet(asset=asset, date=timezone.now())
    #                 initial_media_set.save()
    #         try:
    #             file = self.get(
    #                 self.get_ninox_endpoint_url(table_id=table_id, record_id=record["id"], filename=filename),
    #                 stream=True,
    #             )
    #             self._logger.info(f"Saving file {filename} for {asset}.")
    #
    #             if file:
    #                 media = MediaItem(set_id=initial_media_set.id)
    #                 media.media.save(filename, ContentFile(file.content), save=True)
    #         except Exception as err:
    #             self._logger.error(f"Some error occured: {err}")

    def sync_ninox_record(self, record, category, table_id, with_media=True):
        asset, created, status = self.create_asset(record, category)

        if asset:
            self.update_asset_details(asset, record)
            # if with_media:
            #     self.update_asset_media(asset, record, table_id)

    def full_sync(self, with_media=True):
        tables = self.get(self.get_ninox_endpoint_url())
        for table in tables:
            if not table["name"] in self.ninox_table_to_asset_category:
                continue

            category, _ = self.ninox_table_to_asset_category[table["name"]]
            records = self.get(self.get_ninox_endpoint_url(table_id=table["id"]))
            for record in records:
                self.sync_ninox_record(record, category, table["id"], with_media)

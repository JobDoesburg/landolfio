import logging
from typing import List, Any, Dict, Type

from django.conf import settings

import moneybird
from django.core.exceptions import ValidationError
from moneybird import MoneyBird, TokenAuthentication

from moneybird_accounting.models import MoneybirdSynchronizableResourceModel


class MoneyBirdSynchronizationError(ValidationError):
    pass


# TODO implement webhooks!


class MoneyBirdAPITalker:
    _logger = logging.getLogger("django.moneybird")

    _token = settings.MONEYBIRD_API_TOKEN
    _administration_id = settings.MONEYBIRD_ADMINISTRATION_ID
    _moneybird = MoneyBird(TokenAuthentication(_token))

    @property
    def moneybird(self):
        """An Moneybird API instance (can be adapted to support API sessions)."""
        return self._moneybird

    @property
    def administration_id(self):
        """The administration_id to work with."""
        return self._administration_id

    def sync_objects(self, cls: Type[MoneybirdSynchronizableResourceModel]):
        """Synchronize all objects of a MoneybirdSynchronizableResourceModel."""
        self._logger.info(f"Getting Moneybird {cls.get_moneybird_resource_path_name()} for synchronization")

        data = self.moneybird.get(f"{cls.get_moneybird_resource_path_name()}/synchronization", self.administration_id,)

        self._logger.info(f"Moneybird returned {len(data)} {cls.get_moneybird_resource_path_name()}")

        mapped_objects = cls.objects.filter(id__in=[x["id"] for x in data])

        if len(mapped_objects) > 0:
            self._logger.info(
                f"Mapped {len(mapped_objects)} {cls.get_moneybird_resource_path_name()}: {mapped_objects}"
            )

        to_delete = cls.objects.exclude(id__in=[x["id"] for x in data])
        if len(to_delete) > 0:
            self._logger.info(
                f"Found {len(to_delete)} {cls.get_moneybird_resource_path_name()} to delete: {to_delete}"
            )

        to_delete.delete()

        update_or_create = []
        for obj_data in data:
            try:
                obj = mapped_objects.get(id=obj_data["id"])
            except cls.DoesNotExist:
                self._logger.info(f"Found new {cls.get_moneybird_resource_name()} to create with id {obj_data['id']}")
                update_or_create.append(obj_data["id"])
            else:
                if obj.version != obj_data["version"]:
                    self._logger.info(f"Found {obj} to be updated")
                    update_or_create.append(obj_data["id"])

        return self.update_or_create_objects(cls, update_or_create)

    def update_or_create_objects(self, cls: Type[MoneybirdSynchronizableResourceModel], ids: List[str]):
        """Update or create Moneybird objects with certain ids."""
        chunks = [ids[i : i + 100] for i in range(0, len(ids), 100)]

        for chunk in chunks:
            self._logger.info(
                f"Getting {len(chunk)} Moneybird {cls.get_moneybird_resource_path_name()} by id to sync: {chunk}"
            )

            data = self.moneybird.post(
                f"{cls.get_moneybird_resource_path_name()}/synchronization", {"ids": chunk}, self.administration_id,
            )

            self._logger.info(
                f"Moneybird returned {len(data)} {cls.get_moneybird_resource_path_name()} to create or update: {data}"
            )

            for object_data in data:
                self.update_or_create_object(cls, object_data)

        return cls.objects.filter(id__in=ids)

    def update_or_create_object(self, cls: Type[MoneybirdSynchronizableResourceModel], data: Dict[str, Any]):
        """Update or create a MoneybirdSynchronizableResourceModel object from JSON-like dict values."""
        filtered = dict([(i, data[i]) for i in data if i in cls.get_moneybird_fields()])

        self._logger.info(f"Updating or creating {cls.get_moneybird_resource_path_name()} {data['id']}: {filtered}")

        obj = cls(id=data["id"]).set_moneybird_resource_data(filtered)
        obj.processed = True  # Prevent save() triggering a callback to Moneybird
        obj.save()

        return obj

    def create_moneybird_resource(self, cls: Type[MoneybirdSynchronizableResourceModel], data: Dict[str, Any]):
        """Create a new resource on Moneybird."""
        data_filtered = dict([(x, data[x]) for x in data if x not in cls.get_moneybird_readonly_fields()])
        try:
            self._logger.info(f"Creating Moneybird {cls.get_moneybird_resource_path_name()} {id}: {data_filtered}")
            reply = self.moneybird.post(
                cls.get_moneybird_resource_path_name(),
                {cls.get_moneybird_resource_name(): data_filtered},
                self.administration_id,
            )
            self._logger.info(f"Moneybird returned {cls.get_moneybird_resource_name()}: {reply}")
            return reply
        except moneybird.api.MoneyBird.InvalidData as e:
            raise MoneyBirdSynchronizationError(e.response["error"])

    def patch_moneybird_resource(
        self, cls: Type[MoneybirdSynchronizableResourceModel], id: str, data: Dict[str, Any],
    ):
        """Patch an existing Moneybird resource."""
        data_filtered = dict([(x, data[x]) for x in data if x not in cls.get_moneybird_readonly_fields()])
        try:
            self._logger.info(f"Patching Moneybird {cls.get_moneybird_resource_path_name()} {id}: {data_filtered}")
            reply = self.moneybird.patch(
                f"{cls.get_moneybird_resource_path_name()}/{id}",
                {cls.get_moneybird_resource_name(): data_filtered},
                self.administration_id,
            )
            self._logger.info(f"Moneybird returned {cls.get_moneybird_resource_name()}: {reply}")
            return reply
        except moneybird.api.MoneyBird.InvalidData as e:
            raise MoneyBirdSynchronizationError(e.response["error"])

    def delete_moneybird_resource(self, cls: Type[MoneybirdSynchronizableResourceModel], id: str):
        """Delete an existing Moneybird resource."""
        try:
            self._logger.info(f"Deleting Moneybird {cls.get_moneybird_resource_path_name()} {id}")
            return self.moneybird.delete(f"{cls.get_moneybird_resource_path_name()}/{id}", self.administration_id,)
        except moneybird.api.MoneyBird.APIError as e:
            if e.status_code == 204:
                pass
            else:
                raise MoneyBirdSynchronizationError(e.response)

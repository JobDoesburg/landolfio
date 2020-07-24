import logging
from typing import List, Type

import moneybird
from django.core.exceptions import ValidationError
from django.db import IntegrityError
from moneybird import MoneyBird, TokenAuthentication

from moneybird_accounting.models import *


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

        to_delete = cls.objects.exclude(id__in=[x["id"] for x in data])
        if len(to_delete) > 0:
            self._logger.info(
                f"Found {len(to_delete)} {cls.get_moneybird_resource_path_name()} to delete: {to_delete}"
            )

        for delete_object in to_delete:
            delete_object.processed = True
            delete_object.delete()

        update_or_create = []
        for obj_data in data:
            try:
                obj = cls.objects.get(id=obj_data["id"])
            except cls.DoesNotExist:
                self._logger.info(f"Found new {cls.get_moneybird_resource_name()} to create with id {obj_data['id']}")
                update_or_create.append(obj_data["id"])
            else:
                if obj.version != obj_data["version"]:
                    self._logger.info(f"Found {obj} to be updated")
                    update_or_create.append(obj_data["id"])

        return self.update_or_create_objects(cls, update_or_create)

    def sync_objects_hard(self, cls: Type[MoneybirdSynchronizableResourceModel]):
        self._logger.info(f"Performing hard sync on {cls} objects, setting version to None.")
        cls.objects.update(version=None)

        self.sync_objects(cls)

    def sync_readonly_objects(self, cls: Type[MoneybirdReadOnlyResourceModel]):
        data = self.moneybird.get(f"{cls.get_moneybird_resource_path_name()}", self.administration_id,)

        ids = []
        for obj in data:
            ids.append(obj["id"])
            cls.update_or_create_object_from_moneybird(obj)

        for obj in cls.objects.all():
            if obj.id not in ids:
                obj.processed = True
                obj.delete()

    def sync_readwrite_objects(self, cls: Type[MoneybirdReadWriteResourceModel]):
        data = self.moneybird.get(f"{cls.get_moneybird_resource_path_name()}", self.administration_id,)

        ids = []
        for obj in data:
            ids.append(obj["id"])
            cls.update_or_create_object_from_moneybird(obj)

        for obj in cls.objects.all():
            if obj.id not in ids:
                obj.processed = True
                obj.delete()

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
                self._logger.info(
                    f"Updating or creating {cls.get_moneybird_resource_path_name()} {object_data['id']}: {object_data}"
                )
                cls.update_or_create_object_from_moneybird(object_data)

        return cls.objects.filter(id__in=ids)

    def create_moneybird_resource(self, cls: Type[MoneybirdReadWriteResourceModel], data: Dict[str, Any]):
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
            raise IntegrityError(e.response["error"] if e.response["error"] else e.response)

    def patch_moneybird_resource(
        self, cls: Type[MoneybirdReadWriteResourceModel], id: str, data: Dict[str, Any],
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
            raise IntegrityError(e.response["error"] if e.response["error"] else e.response)

    def delete_moneybird_resource(self, cls: Type[MoneybirdReadWriteResourceModel], id: str):
        """Delete an existing Moneybird resource."""
        try:
            self._logger.info(f"Deleting Moneybird {cls.get_moneybird_resource_path_name()} {id}")
            return self.moneybird.delete(f"{cls.get_moneybird_resource_path_name()}/{id}", self.administration_id,)
        except moneybird.api.MoneyBird.APIError as e:
            if e.status_code == 204:
                pass
            else:
                raise IntegrityError(e.response["error"] if e.response["error"] else e.response)

    def full_sync(self, hard=False):
        for cls in MoneybirdReadOnlyResourceModel.__subclasses__():
            if not cls._meta.abstract:
                self.sync_readonly_objects(cls)
        for cls in MoneybirdReadWriteResourceModel.__subclasses__():
            if not cls._meta.abstract:
                self.sync_readwrite_objects(cls)
        for cls in MoneybirdSynchronizableResourceModel.__subclasses__():
            if not cls._meta.abstract:
                if hard:
                    self.sync_objects_hard(cls)
                else:
                    self.sync_objects(cls)

import logging
import threading
from typing import Generator

from moneybird.administration import (
    Administration,
    get_moneybird_administration,
)
from moneybird.resource_types import (
    MoneybirdResourceId,
    MoneybirdResource,
    MoneybirdResourceVersion,
    ResourceDiff,
    MoneybirdResourceType,
    SynchronizableMoneybirdResourceType,
    get_moneybird_resources,
)

MAX_REQUEST_SIZE = 100

sync_lock = threading.Lock()


class MoneybirdSync:
    @staticmethod
    def __chunks(lst: list, chunk_size: int) -> Generator[list, None, None]:
        """Split a list into chunks of size chunk_size."""
        for idx in range(0, len(lst), chunk_size):
            yield lst[idx : idx + chunk_size]

    def __init__(self, administration: Administration):
        self.administration = administration

    def get_resource_versions(
        self, resource_type: SynchronizableMoneybirdResourceType
    ) -> dict[MoneybirdResourceId, MoneybirdResourceVersion]:
        objects = self.administration.get(
            f"{resource_type.api_path}/synchronization",
        )
        return {instance["id"]: instance["version"] for instance in objects}

    def _get_resources_by_id_paginated(
        self,
        resource_type: SynchronizableMoneybirdResourceType,
        ids: list[MoneybirdResourceId],
    ):
        assert len(ids) <= MAX_REQUEST_SIZE
        return self.administration.post(
            f"{resource_type.api_path}/synchronization", data={"ids": ids}
        )

    def get_resources_by_id(
        self,
        resource_type: SynchronizableMoneybirdResourceType,
        ids: list[MoneybirdResourceId],
    ) -> list[MoneybirdResource]:
        if len(ids) == 0:
            return []

        objects = []

        for id_chunk in self.__chunks(ids, MAX_REQUEST_SIZE):
            try:
                objects.extend(
                    self._get_resources_by_id_paginated(resource_type, id_chunk)
                )
            except Administration.Throttled:
                break
        return objects

    def get_all_resources(self, resource_type: MoneybirdResourceType):
        return self.administration.get(f"{resource_type.api_path}")

    def get_resource_diffs(
        self,
        resource: SynchronizableMoneybirdResourceType,
        local_versions: dict[MoneybirdResourceId, MoneybirdResourceVersion],
    ) -> ResourceDiff:
        remote_versions = self.get_resource_versions(resource)
        resources_to_sync = SynchronizableMoneybirdResourceType.diff_resource_versions(
            local_versions, remote_versions
        )

        resources_diff = ResourceDiff()
        resources_diff.added = self.get_resources_by_id(
            resource, resources_to_sync.added
        )
        resources_diff.changed = self.get_resources_by_id(
            resource, resources_to_sync.changed
        )
        resources_diff.removed = resources_to_sync.removed

        return resources_diff

    def sync_resource_type(self, resource_type: MoneybirdResourceType):
        logging.info(f"Start synchronizing {resource_type.entity_type}")
        local_versions = resource_type.get_local_versions()
        if issubclass(resource_type, SynchronizableMoneybirdResourceType):
            changes = self.get_resource_diffs(resource_type, local_versions)
        else:
            resources = self.get_all_resources(resource_type)
            changes = MoneybirdResourceType.diff_resources(local_versions, resources)
        logging.info(f"Updating {resource_type.entity_type} resources")
        resource_type.update_resources(changes)
        logging.info(f"Finished synchronizing {resource_type.entity_type}")

    def perform_sync(self, resource_types: list[MoneybirdResourceType]):
        for resource_type in resource_types:
            self.sync_resource_type(resource_type)


def synchronize(full_sync=False) -> None:
    locked = sync_lock.acquire(blocking=False)
    if locked:
        try:
            resource_types = get_moneybird_resources()
            administration = get_moneybird_administration()
            if full_sync:
                for resource_type in resource_types:
                    if issubclass(resource_type, SynchronizableMoneybirdResourceType):
                        resource_type.get_queryset().update(moneybird_version=None)

            MoneybirdSync(administration).perform_sync(resource_types)
        finally:
            sync_lock.release()

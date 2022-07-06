import threading
from typing import Generator

from django.conf import settings

from accounting.moneybird.administration import Administration, HttpsAdministration
from accounting.moneybird.resources import (
    MoneybirdResourceId,
    MoneybirdResource,
    MoneybirdResourceVersion,
    MoneybirdResourceTypes,
    ResourceDiff,
    ResourceVersionDiff,
    MoneybirdResourceType,
    SynchronizableMoneybirdResourceType,
)

MAX_REQUEST_SIZE = 100


def chunks(lst: list, chunk_size: int) -> Generator[list, None, None]:
    """Split a list into chunks of size chunk_size."""
    for idx in range(0, len(lst), chunk_size):
        yield lst[idx : idx + chunk_size]


class MoneybirdSync:
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

        for id_chunk in chunks(ids, MAX_REQUEST_SIZE):
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
        local_versions = resource_type.get_local_versions()
        if issubclass(resource_type, SynchronizableMoneybirdResourceType):
            changes = self.get_resource_diffs(resource_type, local_versions)
        else:
            resources = self.get_all_resources(resource_type)
            changes = MoneybirdResourceType.diff_resources(local_versions, resources)
        resource_type.update_resources(changes)

    def perform_sync(self):
        for resource_type in MoneybirdResourceTypes:
            self.sync_resource_type(resource_type)


sync_lock = threading.Lock()


def sync_database() -> None:
    """
    Synchronize the database to the remote MoneyBird administration.

    Get changes from the remote MoneyBird administration and apply them in the database.

    This function expects the following Django settings to be set:
     - MONEYBIRD_ADMINISTRATION_ID
     - MONEYBIRD_API_KEY
    """
    # pylint: disable=consider-using-with
    locked = sync_lock.acquire(blocking=False)
    if locked:
        try:
            administration_id = settings.MONEYBIRD_ADMINISTRATION_ID
            key = settings.MONEYBIRD_API_KEY
            administration = HttpsAdministration(key, administration_id)

            MoneybirdSync(administration).perform_sync()
        finally:
            sync_lock.release()

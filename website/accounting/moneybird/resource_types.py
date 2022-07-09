from dataclasses import dataclass, field

from django.conf import settings
from django.utils.module_loading import import_string

MoneybirdResourceId = str
MoneybirdResourceVersion = int
MoneybirdResource = dict


@dataclass
class ResourceDiff:
    added: list[MoneybirdResource] = field(default_factory=list)
    changed: list[MoneybirdResource] = field(default_factory=list)
    removed: list[MoneybirdResourceId] = field(default_factory=list)


@dataclass
class ResourceVersionDiff:
    added: list[MoneybirdResourceId] = field(default_factory=list)
    changed: list[MoneybirdResourceId] = field(default_factory=list)
    removed: list[MoneybirdResourceId] = field(default_factory=list)


class MoneybirdResourceType:
    entity_type = None
    api_path = None
    synchronizable = None
    model = None

    @classmethod
    def get_queryset(cls):
        return cls.model._default_manager.all()

    @classmethod
    def get_local_versions(cls) -> list[MoneybirdResourceId]:
        return list(
            map(
                MoneybirdResourceId,
                cls.get_queryset().values_list("moneybird_id", flat=True),
            )
        )

    @classmethod
    def get_model_kwargs(cls, data):
        return {"moneybird_id": MoneybirdResourceId(data["id"])}

    @classmethod
    def create_from_moneybird(cls, data: MoneybirdResource):
        return cls.model._default_manager.create(**cls.get_model_kwargs(data))

    @classmethod
    def update_from_moneybird(cls, data: MoneybirdResource):
        return cls.get_queryset().update_or_create(
            moneybird_id=MoneybirdResourceId(data["id"]),
            defaults={**cls.get_model_kwargs(data)},
        )

    @classmethod
    def delete_from_moneybird(cls, resource_id: MoneybirdResourceId):
        return cls.get_queryset().get(moneybird_id=resource_id).delete()

    @classmethod
    def update_resources(cls, diff: ResourceDiff):
        for resource in diff.added:
            cls.create_from_moneybird(resource)
        for resource in diff.changed:
            cls.update_from_moneybird(resource)
        for resource_id in diff.removed:
            cls.delete_from_moneybird(resource_id)

    @staticmethod
    def diff_resources(
        old: list[MoneybirdResourceId], new: list[MoneybirdResource]
    ) -> ResourceDiff:
        resources_diff = ResourceDiff()
        resources_diff.added = list(
            filter(lambda resource: resource["id"] not in old, new)
        )
        resources_diff.changed = list(
            filter(lambda resource: resource["id"] in old, new)
        )  # We can only consider every resource has changed if it is in the new list
        resources_diff.removed = list(
            filter(
                lambda resource: resource not in list(r["id"] for r in new),
                old,
            )
        )
        return resources_diff

    @classmethod
    def process_webhook_event(cls, data: MoneybirdResource, event: str):
        return cls.update_from_moneybird(data)


class SynchronizableMoneybirdResourceType(MoneybirdResourceType):
    @classmethod
    def get_model_kwargs(cls, data):
        kwargs = super().get_model_kwargs(data)
        version = data.get("version", None)
        if version is not None:
            kwargs["moneybird_version"] = MoneybirdResourceVersion(version)
        return kwargs

    @classmethod
    def get_local_versions(cls) -> dict[MoneybirdResourceId, MoneybirdResourceVersion]:
        return dict(
            map(
                lambda x: (
                    MoneybirdResourceId(x[0]),
                    MoneybirdResourceVersion(x[1] or 0),
                ),
                cls.get_queryset().values_list("moneybird_id", "moneybird_version"),
            )
        )

    @staticmethod
    def diff_resource_versions(
        old: dict[MoneybirdResourceId, MoneybirdResourceVersion],
        new: dict[MoneybirdResourceId, MoneybirdResourceVersion],
    ) -> ResourceVersionDiff:
        old_ids = old.keys()
        new_ids = new.keys()

        kept = old_ids & new_ids

        diff = ResourceVersionDiff()
        diff.added = list(new_ids - old_ids)
        diff.removed = list(old_ids - new_ids)
        diff.changed = list(
            filter(lambda doc_id: old[doc_id] != new[doc_id], kept)
        )  # Check if the version has changed

        return diff


class MoneybirdResourceTypeWithDocumentLines(SynchronizableMoneybirdResourceType):
    @classmethod
    def get_local_document_line_versions(cls, document) -> list[MoneybirdResourceId]:
        return list(
            map(
                MoneybirdResourceId,
                cls.get_document_lines_queryset(document).values_list(
                    "moneybird_id", flat=True
                ),
            )
        )

    @classmethod
    def get_document_lines_queryset(cls, document):
        return (
            document.document_lines.all()
        )  # TODO: Make document_lines a property of the model

    @classmethod
    def get_document_line_model_kwargs(cls, line_data: MoneybirdResource):
        return {"moneybird_id": MoneybirdResourceId(line_data["id"])}

    @classmethod
    def create_document_line_from_moneybird(
        cls, document, line_data: MoneybirdResource
    ):
        return cls.get_document_lines_queryset(document).create(
            document=document, **cls.get_document_line_model_kwargs(line_data)
        )

    @classmethod
    def update_document_line_from_moneybird(
        cls, document, line_data: MoneybirdResource
    ):
        return cls.get_document_lines_queryset(document).update_or_create(
            moneybird_id=MoneybirdResourceId(line_data["id"]),
            document=document,
            defaults={**cls.get_document_line_model_kwargs(line_data)},
        )

    @classmethod
    def delete_document_line_from_moneybird(
        cls, document, resource_id: MoneybirdResourceId
    ):
        return (
            cls.get_document_lines_queryset(document)
            .get(moneybird_id=resource_id)
            .delete()
        )

    @classmethod
    def update_document_lines(cls, document, document_lines_diff: ResourceDiff):
        for document_line in document_lines_diff.added:
            cls.create_document_line_from_moneybird(document, document_line)
        for document_line in document_lines_diff.changed:
            cls.update_document_line_from_moneybird(document, document_line)
        for document_line_id in document_lines_diff.removed:
            cls.delete_document_line_from_moneybird(document, document_line_id)

    @classmethod
    def get_document_line_resource_data(
        cls, data: MoneybirdResource
    ) -> list[MoneybirdResource]:
        return data["details"]

    @classmethod
    def create_from_moneybird(cls, data: MoneybirdResource):
        document = super().create_from_moneybird(data)
        document_lines = cls.get_document_line_resource_data(data)
        for line_data in document_lines:
            cls.create_document_line_from_moneybird(document, line_data)

    @classmethod
    def update_from_moneybird(cls, data: MoneybirdResource):
        document, _ = super().update_from_moneybird(data)
        new_lines = cls.get_document_line_resource_data(data)
        old_lines = cls.get_local_document_line_versions(document)
        document_lines_diff = cls.diff_resources(old_lines, new_lines)
        cls.update_document_lines(document, document_lines_diff)


def get_moneybird_resources():
    return [
        import_string(resource_type)
        for resource_type in settings.MONEYBIRD_RESOURCE_TYPES
    ]

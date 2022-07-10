from dataclasses import dataclass, field

from django.conf import settings
from django.utils.module_loading import import_string

from moneybird.administration import get_moneybird_administration

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
    entity_type_name = None
    api_path = None
    synchronizable = None
    model = None
    can_write = True
    can_delete = True

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
    def create_from_moneybird(cls, resource_data: MoneybirdResource):
        obj = cls.model(**cls.get_model_kwargs(resource_data))
        obj.save(push_to_moneybird=False)
        return obj

    @classmethod
    def update_from_moneybird(cls, resource_data: MoneybirdResource):
        try:
            obj = cls.get_queryset().get(
                moneybird_id=MoneybirdResourceId(resource_data["id"])
            )
        except cls.model.DoesNotExist:
            return cls.create_from_moneybird(resource_data), True

        obj.update_fields_from_moneybird(resource_data)
        obj.save(push_to_moneybird=False)

        return obj, False

    @classmethod
    def delete_from_moneybird(cls, resource_id: MoneybirdResourceId):
        return (
            cls.get_queryset()
            .get(moneybird_id=resource_id)
            .delete(delete_on_moneybird=False)
        )

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

    @classmethod
    def serialize_for_moneybird(cls, instance):
        return {
            "id": MoneybirdResourceId(instance.moneybird_id),
        }

    @classmethod
    def push_to_moneybird(cls, instance, data=None):
        if not cls.can_write:
            return None

        if data is None:
            data = cls.serialize_for_moneybird(instance)

        if data == {} or data is None:
            return None

        content = {cls.entity_type_name: data}
        administration = get_moneybird_administration()

        if instance.moneybird_id is None:
            returned_data = administration.post(cls.api_path, content)
        else:
            returned_data = administration.patch(
                f"{cls.api_path}/{instance.moneybird_id}", content
            )

        instance.update_fields_from_moneybird(returned_data)

        return returned_data

    @classmethod
    def delete_on_moneybird(cls, instance):
        if not cls.can_delete:
            return None
        if not instance.moneybird_id:
            return None

        administration = get_moneybird_administration()
        return administration.delete(f"{cls.api_path}/{instance.moneybird_id}")

    @classmethod
    def get_from_moneybird(cls, instance):
        if not instance.moneybird_id:
            return None

        administration = get_moneybird_administration()
        data = administration.get(f"{cls.api_path}/{instance.moneybird_id}")

        cls.update_from_moneybird(data)

        instance.update_fields_from_moneybird(data)
        return data


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
    document_lines_model = None
    document_lines_foreign_key = "document_lines"
    document_foreign_key = "document"
    document_lines_resource_data_name = "details"
    document_lines_attributes_name = "details_attributes"

    @classmethod
    def get_local_document_line_versions(cls, document) -> list[MoneybirdResourceId]:
        return list(
            map(
                MoneybirdResourceId,
                cls.get_document_lines_queryset(document)
                .exclude(moneybird_id__isnull=True)
                .values_list("moneybird_id", flat=True),
            )
        )

    @classmethod
    def get_document_lines_queryset(cls, document):
        return getattr(document, cls.document_lines_foreign_key).all()

    @classmethod
    def get_document_line_model_kwargs(cls, line_data: MoneybirdResource, document):
        return {"moneybird_id": MoneybirdResourceId(line_data["id"])}

    @classmethod
    def create_document_line_from_moneybird(
        cls, document, line_data: MoneybirdResource
    ):
        obj = cls.document_lines_model(
            **cls.get_document_line_model_kwargs(line_data, document)
        )
        obj.save(push_to_moneybird=False)
        return obj

    @classmethod
    def update_document_line_from_moneybird(
        cls, document, line_data: MoneybirdResource
    ):
        try:
            obj = cls.get_document_lines_queryset(document).get(
                moneybird_id=MoneybirdResourceId(line_data["id"])
            )
        except cls.model.DoesNotExist:
            return cls.create_document_line_from_moneybird(document, line_data), True

        obj.update_fields_from_moneybird(line_data)
        obj.save(push_to_moneybird=False)

        return obj, False

    @classmethod
    def delete_document_line_from_moneybird(
        cls, document, resource_id: MoneybirdResourceId
    ):
        return (
            cls.get_document_lines_queryset(document)
            .get(moneybird_id=resource_id)
            .delete(delete_on_moneybird=False)
        )

    @classmethod
    def update_document_lines(cls, document, document_lines_diff: ResourceDiff):
        for document_line in document_lines_diff.added:
            cls.create_document_line_from_moneybird(document, document_line)
        for document_line in document_lines_diff.changed:
            cls.update_document_line_from_moneybird(document, document_line)
        for document_line_id in document_lines_diff.removed:
            cls.delete_document_line_from_moneybird(document, document_line_id)

        cls.get_document_lines_queryset(document).filter(
            moneybird_id__isnull=True
        ).delete()

    @classmethod
    def get_document_line_resource_data(
        cls, data: MoneybirdResource
    ) -> list[MoneybirdResource]:
        return data[cls.document_lines_resource_data_name]

    @classmethod
    def create_from_moneybird(cls, resource_data: MoneybirdResource):
        document = super().create_from_moneybird(resource_data)
        document_lines = cls.get_document_line_resource_data(resource_data)
        for line_data in document_lines:
            cls.create_document_line_from_moneybird(document, line_data)

    @classmethod
    def update_from_moneybird(cls, resource_data: MoneybirdResource):
        document, _ = super().update_from_moneybird(resource_data)
        new_lines = cls.get_document_line_resource_data(resource_data)
        old_lines = cls.get_local_document_line_versions(document)
        document_lines_diff = cls.diff_resources(old_lines, new_lines)
        cls.update_document_lines(document, document_lines_diff)

    @classmethod
    def serialize_document_line_for_moneybird(cls, document_line, document):
        if document_line.moneybird_id:
            return {"id": MoneybirdResourceId(document_line.moneybird_id)}
        return {}

    @classmethod
    def serialize_document_lines_for_moneybird(cls, instance):
        return {
            cls.document_lines_attributes_name: list(
                cls.serialize_document_line_for_moneybird(line, instance)
                for line in cls.get_document_lines_queryset(instance)
            )
        }

    @classmethod
    def serialize_for_moneybird(cls, instance):
        data = super().serialize_for_moneybird(instance)
        data.update(cls.serialize_document_lines_for_moneybird(instance))
        return data

    @classmethod
    def push_document_line_to_moneybird(cls, document_line, document, data=None):
        if data is None:
            data = cls.serialize_document_line_for_moneybird(document_line, document)
        request_data = {cls.document_lines_attributes_name: [data]}
        returned_data = cls.push_to_moneybird(document, request_data)
        document.save(push_to_moneybird=False)
        return returned_data

    @classmethod
    def delete_document_line_on_moneybird(cls, document_line, document):
        if not document_line.moneybird_id:
            return

        document_line_data = {
            "id": MoneybirdResourceId(document_line.moneybird_id),
            "_destroy": True,
        }
        data = {cls.document_lines_attributes_name: [document_line_data]}
        returned_data = cls.push_to_moneybird(document, data)
        document.save(push_to_moneybird=False)
        return returned_data


def get_moneybird_resources():
    return [
        import_string(resource_type)
        for resource_type in settings.MONEYBIRD_RESOURCE_TYPES
    ]


def get_moneybird_resource_for_model(model):
    for resource_type in get_moneybird_resources():
        if resource_type.model == model:
            return resource_type


def get_moneybird_resource_for_document_lines_model(model):
    for resource_type in get_moneybird_resources():
        if (
            issubclass(resource_type, MoneybirdResourceTypeWithDocumentLines)
            and resource_type.document_lines_model == model
        ):
            return resource_type


def get_moneybird_resource_type_for_webhook_entity(entity_type):
    for resource_type in get_moneybird_resources():
        if resource_type.entity_type == entity_type:
            return resource_type

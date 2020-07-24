from django.db.models.signals import pre_save, pre_delete
from django.dispatch import receiver

from moneybird_accounting.models.moneybird_resource import (
    MoneybirdNestedDataResourceModel,
    MoneybirdReadWriteResourceModel,
)
from moneybird_accounting.moneybird_sync import MoneyBirdAPITalker


def dict_changes(old_data, new_data):
    """Calculate the data difference for 2 objects."""
    return dict(
        [
            (x, new_data[x])
            if new_data[x] is not None
            else (x, "")  # If a field is emptied, '' should be patched instead of None
            for x in new_data
            if x not in old_data  # Patch new data
            or (
                new_data[x] != old_data[x] and not (new_data[x] is None and old_data[x] == "")
            )  # and changed data, where '' and None are considered equal
            or (x == "id" and not (new_data[x] is None or new_data[x] == ""))  # Always include the id if present
        ]
    )


@receiver(pre_save)
def update_or_create_moneybird_resource_on_save(sender, instance, **kwargs):
    if not issubclass(sender, MoneybirdReadWriteResourceModel):
        return

    if instance.processed:  # Prevent triggering another Moneybird call on synchronization
        instance.processed = False
        return

    m = MoneyBirdAPITalker()
    new_data = instance.get_moneybird_resource_data()

    try:
        obj = sender.objects.get(pk=instance.pk)
    except sender.DoesNotExist:
        if new_data["id"] is None or new_data["id"] == "":
            del new_data["id"]

        moneybird_obj = m.create_moneybird_resource(sender, new_data)
    else:
        old_data = obj.get_moneybird_resource_data()
        changes = dict_changes(old_data, new_data)

        if not changes or changes == {} or ("id" in changes and len(changes) == 1):
            return

        obj_id = new_data["id"]
        moneybird_obj = m.patch_moneybird_resource(sender, obj_id, changes)

    instance.set_moneybird_resource_data(moneybird_obj)


@receiver(pre_save)
def update_or_create_moneybird_nested_data_on_save(sender, instance, **kwargs):
    if not issubclass(sender, MoneybirdNestedDataResourceModel):
        return

    if instance.processed:  # Prevent triggering another Moneybird call on synchronization
        instance.processed = False
        return

    parent = instance.get_moneybird_attr(sender.get_moneybird_nested_foreign_key())
    data = {}

    new_data = instance.get_moneybird_resource_data()

    try:
        obj = sender.objects.get(pk=instance.pk)
    except sender.DoesNotExist:
        if new_data["id"] is None or new_data["id"] == "":
            del new_data["id"]

        data[sender.get_moneybird_resource_name() + "_attributes"] = [new_data]
    else:
        old_data = obj.get_moneybird_resource_data()
        changes = dict_changes(old_data, new_data)
        data[sender.get_moneybird_resource_name() + "_attributes"] = [changes]

        if not changes or changes == {} or ("id" in changes and len(changes) == 1):
            return

    m = MoneyBirdAPITalker()
    moneybird_obj = m.patch_moneybird_resource(type(parent), parent.id, data)

    for returned_data in moneybird_obj[instance.get_moneybird_resource_name()]:
        if returned_data["id"] == instance.id or instance.id is None or instance.id == "":
            instance.set_moneybird_resource_data(returned_data)

    parent.set_moneybird_resource_data(moneybird_obj)
    parent.processed = True
    parent.save()


@receiver(pre_delete)
def delete_moneybird_resource_on_delete(sender, instance, **kwargs):
    if not issubclass(sender, MoneybirdReadWriteResourceModel):
        return

    if instance.processed:  # Prevent triggering another Moneybird call on synchronization
        instance.processed = False
        return

    m = MoneyBirdAPITalker()
    m.delete_moneybird_resource(sender, instance.id)


@receiver(pre_delete)
def delete_moneybird_resource_nested_data_on_delete(sender, instance, **kwargs):
    if not issubclass(sender, MoneybirdNestedDataResourceModel):
        return

    if instance.processed:  # Prevent triggering another Moneybird call on synchronization
        instance.processed = False
        return

    parent = instance.get_moneybird_attr(sender.get_moneybird_nested_foreign_key())

    new_data = {"id": instance.id, "_destroy": "true"}

    data = {sender.get_moneybird_resource_name() + "_attributes": [new_data]}

    m = MoneyBirdAPITalker()
    m.patch_moneybird_resource(type(parent), parent.id, data)

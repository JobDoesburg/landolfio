from django.db.models.signals import pre_save, pre_delete
from django.dispatch import receiver

from moneybird_accounting.models import MoneybirdSynchronizableResourceModel
from moneybird_accounting.moneybird_sync import MoneyBirdAPITalker


@receiver(pre_save)
def update_or_create_moneybird_resource_on_save(sender, instance, **kwargs):
    if not issubclass(sender, MoneybirdSynchronizableResourceModel):
        return

    if instance.processed:  # Prevent triggering another Moneybird call on synchronization
        instance.processed = False
        return

    m = MoneyBirdAPITalker()
    try:
        obj = sender.objects.get(pk=instance.pk)
    except sender.DoesNotExist:
        moneybird_obj = m.create_moneybird_resource(sender, instance.get_moneybird_resource_data())
    else:
        new_data = instance.get_moneybird_resource_data()
        old_data = obj.get_moneybird_resource_data()
        changes = dict(
            [
                (x, new_data[x])
                if new_data[x] is not None
                else (x, "")  # If a field is emptied, '' should be patched instead of None
                for x in new_data
                if x not in old_data  # Patch new data
                or (
                    new_data[x] != old_data[x] and not (new_data[x] is None and old_data[x] == "")
                )  # and changed data, where '' and None are considered equal
            ]
        )

        if not changes:
            return

        obj_id = new_data["id"]
        moneybird_obj = m.patch_moneybird_resource(sender, obj_id, changes)

    instance.set_moneybird_resource_data(moneybird_obj)


@receiver(pre_delete)
def delete_moneybird_resource_on_delete(sender, instance, **kwargs):
    if not issubclass(sender, MoneybirdSynchronizableResourceModel):
        return

    m = MoneyBirdAPITalker()
    m.delete_moneybird_resource(sender, instance.id)

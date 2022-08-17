from django.core.management.base import BaseCommand

from scantags.models import ScanTag


class Command(BaseCommand):
    help = "Generate tags"

    def add_arguments(self, parser):
        parser.add_argument("amount", type=int)

    def handle(self, *args, **options):
        amount = options["amount"]
        for _ in range(amount):
            new_id = ScanTag.generate_new_id()
            tag = ScanTag(id=new_id)
            tag.full_clean()
            tag.save()
            self.stdout.write(self.style.NOTICE("New tag generated: {}".format(new_id)))
        self.stdout.write(self.style.SUCCESS(f"Successfully created {amount} tags."))

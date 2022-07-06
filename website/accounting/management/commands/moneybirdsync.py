from django.core.management.base import BaseCommand

from accounting.services import sync_moneybird


class Command(BaseCommand):
    help = "Synchronize with Moneybird"

    def add_arguments(self, parser):
        parser.add_argument(
            "--full",
            action="store_true",
            help="Perform a full sync without using already stored versions",
        )

    def handle(self, *args, **options):
        sync_moneybird(full_sync=options["full"])
        self.stdout.write(
            self.style.SUCCESS("Successfully synchronized with Moneybird")
        )

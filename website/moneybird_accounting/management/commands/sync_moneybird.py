from django.core.management import BaseCommand

from moneybird_accounting.moneybird_sync import MoneyBirdAPITalker


class Command(BaseCommand):
    def add_arguments(self, parser):
        """Arguments for the command."""
        parser.add_argument(
            "--hard", action="store_true", dest="hard", default=False, help="Perform a hard sync.",
        )

    def handle(self, *args, **options):
        """Execute the command."""
        MoneyBirdAPITalker().full_sync(options["hard"])

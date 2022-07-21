from django.core.management import BaseCommand

from ninox_import.ninox_sync import NinoxImporter


class Command(BaseCommand):
    def add_arguments(self, parser):
        """Arguments for the command."""
        parser.add_argument(
            "--quick",
            action="store_true",
            dest="quick",
            default=False,
            help="Do a quick sync without media files.",
        )

    def handle(self, *args, **options):
        """Execute the command."""
        NinoxImporter().full_sync(with_media=not (options["quick"]))
        self.stdout.write(self.style.SUCCESS("Successfully synchronized with Ninox"))

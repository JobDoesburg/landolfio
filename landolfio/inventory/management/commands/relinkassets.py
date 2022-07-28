from django.core.management.base import BaseCommand

from inventory.services import relink_document_lines_to_assets


class Command(BaseCommand):
    help = "Relink all document lines to assets"

    def handle(self, *args, **options):
        relink_document_lines_to_assets()
        self.stdout.write(
            self.style.SUCCESS(f"Successfully relinked document lines to assets.")
        )

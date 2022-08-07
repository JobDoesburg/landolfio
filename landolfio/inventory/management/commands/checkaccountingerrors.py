from django.core.management.base import BaseCommand

from inventory.services import check_accounting_errors


class Command(BaseCommand):
    help = "Check accounting errors"

    def handle(self, *args, **options):
        errors = check_accounting_errors()
        if errors:
            for error in errors:
                self.stdout.write(self.style.WARNING(error))
        else:
            self.stdout.write(self.style.SUCCESS(f"No accounting errors found."))

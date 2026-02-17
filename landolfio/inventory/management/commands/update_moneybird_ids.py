import json
from django.core.management.base import BaseCommand, CommandError
from inventory.models import Asset
from inventory.moneybird import MoneybirdAssetService


class Command(BaseCommand):
    help = "Update asset moneybird_asset_id from a JSON file"

    def add_arguments(self, parser):
        parser.add_argument(
            'json_file',
            type=str,
            help='Path to JSON file with asset moneybird IDs'
        )

    def handle(self, *args, **options):
        json_file = options['json_file']

        try:
            with open(json_file, 'r') as f:
                data = json.load(f)
        except FileNotFoundError:
            raise CommandError(f'File "{json_file}" not found')
        except json.JSONDecodeError as e:
            raise CommandError(f'Invalid JSON file: {e}')

        updated_count = 0
        not_found_count = 0
        skipped_count = 0

        for asset_name, asset_data in data.items():
            moneybird_id = asset_data.get('moneybird_id')

            if not moneybird_id:
                self.stdout.write(
                    self.style.WARNING(f'Skipping {asset_name}: no moneybird_id')
                )
                skipped_count += 1
                continue

            try:
                asset = Asset.objects.get(name=asset_name)
                asset.moneybird_asset_id = int(moneybird_id)
                asset.save(update_fields=['moneybird_asset_id'])

                try:
                    mb = MoneybirdAssetService()
                    mb.update_asset(asset_id=asset.moneybird_asset_id, name=str(asset))
                    asset.refresh_from_moneybird()
                    self.stdout.write(
                        self.style.SUCCESS(f'Updated {asset_name}: {moneybird_id}, synced name to Moneybird, and refreshed data')
                    )
                except Exception as e:
                    self.stdout.write(
                        self.style.WARNING(f'Updated {asset_name}: {moneybird_id} but failed to sync: {e}')
                    )

                updated_count += 1
            except Asset.DoesNotExist:
                self.stdout.write(
                    self.style.ERROR(f'Asset not found: {asset_name}')
                )
                not_found_count += 1

        self.stdout.write(
            self.style.SUCCESS(
                f'\nCompleted: {updated_count} updated, {not_found_count} not found, {skipped_count} skipped'
            )
        )
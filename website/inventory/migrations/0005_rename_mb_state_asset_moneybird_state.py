# Generated by Django 4.0.4 on 2022-05-25 10:32
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("inventory", "0004_alter_asset_mb_state_alter_asset_local_state"),
    ]

    operations = [
        migrations.RenameField(
            model_name="asset",
            old_name="MB_state",
            new_name="moneybird_state",
        ),
    ]
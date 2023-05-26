# Generated by Django 4.1.7 on 2023-05-26 20:22

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("inventory", "0003_alter_asset_name"),
    ]

    operations = [
        migrations.AddField(
            model_name="asset",
            name="location_nr",
            field=models.PositiveSmallIntegerField(
                blank=True, null=True, verbose_name="location nr"
            ),
        ),
    ]

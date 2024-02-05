# Generated by Django 4.2.9 on 2024-02-05 20:20

from django.db import migrations, models
import inventory.models.attachment


class Migration(migrations.Migration):

    dependencies = [
        ("inventory", "0004_asset_location_nr"),
    ]

    operations = [
        migrations.AlterField(
            model_name="attachment",
            name="attachment",
            field=models.FileField(
                max_length=255,
                upload_to=inventory.models.attachment.attachments_directory_path,
                verbose_name="attachment",
            ),
        ),
        migrations.AlterField(
            model_name="attachment",
            name="upload_date",
            field=models.DateField(
                auto_now_add=True, max_length=255, verbose_name="upload date"
            ),
        ),
    ]
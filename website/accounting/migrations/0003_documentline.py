# Generated by Django 4.0.3 on 2022-04-13 14:49
import django.db.models.deletion
from django.db import migrations
from django.db import models


class Migration(migrations.Migration):

    dependencies = [
        ("accounting", "0002_document_delete_invoice_delete_receipt"),
    ]

    operations = [
        migrations.CreateModel(
            name="DocumentLine",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("json_MB", models.JSONField(verbose_name="JSON MoneyBird")),
                (
                    "document",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="accounting.document",
                        verbose_name="Document",
                    ),
                ),
            ],
        ),
    ]

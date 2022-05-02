# Generated by Django 4.0.4 on 2022-05-02 13:13
from django.db import migrations
from django.db import models


class Migration(migrations.Migration):

    dependencies = [
        ("accounting", "0002_documentline_asset"),
    ]

    operations = [
        migrations.AddField(
            model_name="document",
            name="link",
            field=models.URLField(
                blank=True, null=True, verbose_name="Moneybird document"
            ),
        ),
        migrations.AddField(
            model_name="documentline",
            name="ledger",
            field=models.CharField(
                blank=True,
                choices=[
                    ("Voorraad marge", "Voorraad marge"),
                    ("Voorraad niet-marge", "Voorraad niet-marge"),
                    (
                        "Voorraadwaarde bij verkoop marge",
                        "Voorraadwaarde bij verkoop marge",
                    ),
                    (
                        "Voorraadwaarde bij verkoop niet-marge",
                        "Voorraadwaarde bij verkoop niet-marge",
                    ),
                    ("Verkoop marge", "Verkoop marge"),
                    ("Verkoop niet-marge", "Verkoop niet-marge"),
                    (
                        "Directe afschrijving bij aankoop",
                        "Directe afschrijving bij aankoop",
                    ),
                    ("Afschrijvingen", "Afschrijvingen"),
                    ("Borgen", "Borgen"),
                ],
                max_length=40,
                null=True,
            ),
        ),
    ]

# Generated by Django 4.0.4 on 2022-05-10 12:29
import accounting.models
from django.db import migrations
from django.db import models


class Migration(migrations.Migration):

    dependencies = [
        ("accounting", "0004_alter_document_kind"),
    ]

    operations = [
        migrations.AlterField(
            model_name="documentline",
            name="ledger",
            field=models.CharField(
                choices=[
                    ("VOORRAAD_MARGE", "Voorraad marge"),
                    ("VOORRAAD_NIET_MARGE", "Voorraad niet-marge"),
                    ("VOORRAAD_BIJ_VERKOOP_MARGE", "Voorraadwaarde bij verkoop marge"),
                    (
                        "VOORRAAD_BIJ_VERKOOP_NIET_MARGE",
                        "Voorraadwaarde bij verkoop niet-marge",
                    ),
                    ("VERKOOP_MARGE", "Verkoop marge"),
                    ("VERKOOP_NIET_MARGE", "Verkoop niet-marge"),
                    ("DIRECTE_AFSCHRIJVING", "Directe afschrijving bij aankoop"),
                    ("AFSCHRIJVINGEN", "Afschrijvingen"),
                    ("BORGEN", "Borgen"),
                    ("UNKNOWN", "Onbekend"),
                ],
                default=accounting.models.LedgerAccountId["UNKNOWN"],
                max_length=100,
            ),
        ),
    ]

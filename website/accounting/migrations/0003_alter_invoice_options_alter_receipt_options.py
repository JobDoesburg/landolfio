# Generated by Django 4.0.2 on 2022-03-14 12:26
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("accounting", "0002_invoice_asset_receipt_asset"),
    ]

    operations = [
        migrations.AlterModelOptions(
            name="invoice",
            options={},
        ),
        migrations.AlterModelOptions(
            name="receipt",
            options={},
        ),
    ]
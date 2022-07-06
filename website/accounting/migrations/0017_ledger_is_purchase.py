# Generated by Django 4.0.6 on 2022-07-06 21:33

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("accounting", "0016_ledger_is_margin_ledger_is_sales"),
    ]

    operations = [
        migrations.AddField(
            model_name="ledger",
            name="is_purchase",
            field=models.BooleanField(
                default=False, help_text="Ledger account is used for purchasing assets."
            ),
        ),
    ]
# Generated by Django 4.0.6 on 2022-07-06 13:29

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("accounting", "0002_alter_documentline_document"),
    ]

    operations = [
        migrations.AlterModelOptions(
            name="ledger",
            options={
                "verbose_name": "Ledger account",
                "verbose_name_plural": "Ledger accounts",
            },
        ),
        migrations.AddField(
            model_name="ledger",
            name="account_type",
            field=models.CharField(
                choices=[
                    ("NON_CURRENT_ASSETS", "non current assets"),
                    ("CURRENT_ASSETS", "current assets"),
                    ("EQUITY", "equity"),
                    ("PROVISIONS", "provisions"),
                    ("NON_CURRENT_LIABILITIES", "non current liabilities"),
                    ("CURRENT_LIABILITIES", "current liabilities"),
                    ("REVENUE", "revenue"),
                    ("DIRECT_COSTS", "direct costs"),
                    ("EXPENSES", "expenses"),
                    ("OTHER_INCOME_EXPENSES", "other income expenses"),
                ],
                max_length=100,
                null=True,
                unique=True,
                verbose_name="Account type",
            ),
        ),
    ]

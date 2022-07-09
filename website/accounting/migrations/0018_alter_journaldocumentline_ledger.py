# Generated by Django 4.0.6 on 2022-07-09 11:49

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("accounting", "0017_ledger_is_purchase"),
    ]

    operations = [
        migrations.AlterField(
            model_name="journaldocumentline",
            name="ledger",
            field=models.ForeignKey(
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                to="accounting.ledger",
                verbose_name="Grootboekrekening",
            ),
        ),
    ]

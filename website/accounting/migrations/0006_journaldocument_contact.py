# Generated by Django 4.0.6 on 2022-07-06 13:45

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("accounting", "0005_alter_ledger_account_type"),
    ]

    operations = [
        migrations.AddField(
            model_name="journaldocument",
            name="contact",
            field=models.ForeignKey(
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="journal_documents",
                to="accounting.contact",
                verbose_name="Contact",
            ),
        ),
    ]

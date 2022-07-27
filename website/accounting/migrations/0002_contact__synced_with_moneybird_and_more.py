# Generated by Django 4.0.6 on 2022-07-25 19:20

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("accounting", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="contact",
            name="_synced_with_moneybird",
            field=models.BooleanField(
                default=False, verbose_name="Synced with Moneybird"
            ),
        ),
        migrations.AddField(
            model_name="documentstyle",
            name="_synced_with_moneybird",
            field=models.BooleanField(
                default=False, verbose_name="Synced with Moneybird"
            ),
        ),
        migrations.AddField(
            model_name="estimate",
            name="_synced_with_moneybird",
            field=models.BooleanField(
                default=False, verbose_name="Synced with Moneybird"
            ),
        ),
        migrations.AddField(
            model_name="estimatedocumentline",
            name="_synced_with_moneybird",
            field=models.BooleanField(
                default=False, verbose_name="Synced with Moneybird"
            ),
        ),
        migrations.AddField(
            model_name="generaljournaldocument",
            name="_synced_with_moneybird",
            field=models.BooleanField(
                default=False, verbose_name="Synced with Moneybird"
            ),
        ),
        migrations.AddField(
            model_name="journaldocumentline",
            name="_synced_with_moneybird",
            field=models.BooleanField(
                default=False, verbose_name="Synced with Moneybird"
            ),
        ),
        migrations.AddField(
            model_name="ledgeraccount",
            name="_synced_with_moneybird",
            field=models.BooleanField(
                default=False, verbose_name="Synced with Moneybird"
            ),
        ),
        migrations.AddField(
            model_name="product",
            name="_synced_with_moneybird",
            field=models.BooleanField(
                default=False, verbose_name="Synced with Moneybird"
            ),
        ),
        migrations.AddField(
            model_name="project",
            name="_synced_with_moneybird",
            field=models.BooleanField(
                default=False, verbose_name="Synced with Moneybird"
            ),
        ),
        migrations.AddField(
            model_name="purchasedocument",
            name="_synced_with_moneybird",
            field=models.BooleanField(
                default=False, verbose_name="Synced with Moneybird"
            ),
        ),
        migrations.AddField(
            model_name="recurringsalesinvoice",
            name="_synced_with_moneybird",
            field=models.BooleanField(
                default=False, verbose_name="Synced with Moneybird"
            ),
        ),
        migrations.AddField(
            model_name="recurringsalesinvoicedocumentline",
            name="_synced_with_moneybird",
            field=models.BooleanField(
                default=False, verbose_name="Synced with Moneybird"
            ),
        ),
        migrations.AddField(
            model_name="salesinvoice",
            name="_synced_with_moneybird",
            field=models.BooleanField(
                default=False, verbose_name="Synced with Moneybird"
            ),
        ),
        migrations.AddField(
            model_name="subscription",
            name="_synced_with_moneybird",
            field=models.BooleanField(
                default=False, verbose_name="Synced with Moneybird"
            ),
        ),
        migrations.AddField(
            model_name="taxrate",
            name="_synced_with_moneybird",
            field=models.BooleanField(
                default=False, verbose_name="Synced with Moneybird"
            ),
        ),
        migrations.AddField(
            model_name="workflow",
            name="_synced_with_moneybird",
            field=models.BooleanField(
                default=False, verbose_name="Synced with Moneybird"
            ),
        ),
    ]

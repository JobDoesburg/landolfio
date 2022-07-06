# Generated by Django 4.0.6 on 2022-07-06 19:09

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("accounting", "0009_journaldocument_total_paid_and_more"),
    ]

    operations = [
        migrations.AddField(
            model_name="estimate",
            name="total_price",
            field=models.DecimalField(
                decimal_places=4, max_digits=19, null=True, verbose_name="total price"
            ),
        ),
        migrations.AddField(
            model_name="recurringsalesinvoice",
            name="total_price",
            field=models.DecimalField(
                decimal_places=4, max_digits=19, null=True, verbose_name="total price"
            ),
        ),
    ]

# Generated by Django 4.0.6 on 2022-07-06 19:06

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("accounting", "0008_alter_estimate_workflow_and_more"),
    ]

    operations = [
        migrations.AddField(
            model_name="journaldocument",
            name="total_paid",
            field=models.DecimalField(
                decimal_places=4, max_digits=19, null=True, verbose_name="total paid"
            ),
        ),
        migrations.AddField(
            model_name="journaldocument",
            name="total_price",
            field=models.DecimalField(
                decimal_places=4, max_digits=19, null=True, verbose_name="total price"
            ),
        ),
        migrations.AddField(
            model_name="journaldocument",
            name="total_unpaid",
            field=models.DecimalField(
                decimal_places=4, max_digits=19, null=True, verbose_name="total unpaid"
            ),
        ),
    ]

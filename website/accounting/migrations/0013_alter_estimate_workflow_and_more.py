# Generated by Django 4.0.6 on 2022-07-06 20:11

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("accounting", "0012_alter_estimate_total_price_and_more"),
    ]

    operations = [
        migrations.AlterField(
            model_name="estimate",
            name="workflow",
            field=models.ForeignKey(
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                to="accounting.workflow",
                verbose_name="Workflow",
            ),
        ),
        migrations.AlterField(
            model_name="journaldocument",
            name="workflow",
            field=models.ForeignKey(
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                to="accounting.workflow",
                verbose_name="Workflow",
            ),
        ),
        migrations.AlterField(
            model_name="recurringsalesinvoice",
            name="workflow",
            field=models.ForeignKey(
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                to="accounting.workflow",
                verbose_name="Workflow",
            ),
        ),
    ]

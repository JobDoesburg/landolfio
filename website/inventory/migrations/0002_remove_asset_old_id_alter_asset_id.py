# Generated by Django 4.0.3 on 2022-04-21 10:22
from django.db import migrations
from django.db import models


class Migration(migrations.Migration):

    dependencies = [
        ("inventory", "0001_initial"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="asset",
            name="old_id",
        ),
        migrations.AlterField(
            model_name="asset",
            name="id",
            field=models.CharField(
                max_length=200, primary_key=True, serialize=False, verbose_name="ID"
            ),
        ),
    ]
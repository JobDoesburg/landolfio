# Generated by Django 4.0.6 on 2022-07-27 12:09

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("accounting", "0005_contact__delete_from_moneybird_and_more"),
    ]

    operations = [
        migrations.AlterModelOptions(
            name="project",
            options={"base_manager_name": "objects"},
        ),
        migrations.AlterModelOptions(
            name="taxrate",
            options={"base_manager_name": "objects"},
        ),
    ]
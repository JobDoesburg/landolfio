# Generated by Django 4.0.6 on 2022-07-21 12:35

from django.db import migrations
import django_countries.fields


class Migration(migrations.Migration):

    dependencies = [
        ("accounting", "0003_contact_address_1_contact_address_2_and_more"),
    ]

    operations = [
        migrations.AlterField(
            model_name="contact",
            name="country",
            field=django_countries.fields.CountryField(default="NL", max_length=2),
        ),
    ]

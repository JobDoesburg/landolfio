# Generated by Django 4.0.6 on 2022-07-21 12:48

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('accounting', '0004_alter_contact_country'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='contact',
            name='moneybird_json',
        ),
    ]

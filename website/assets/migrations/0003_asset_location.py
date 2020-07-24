# Generated by Django 3.0.8 on 2020-07-24 21:10

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('assets', '0002_auto_20200724_2307'),
    ]

    operations = [
        migrations.AddField(
            model_name='asset',
            name='location',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, to='assets.AssetLocation'),
        ),
    ]

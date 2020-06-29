# Generated by Django 3.0.5 on 2020-06-29 21:24

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('assets', '0002_auto_20200629_2320'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='assettype',
            options={'verbose_name': 'type', 'verbose_name_plural': 'types'},
        ),
        migrations.AlterField(
            model_name='asset',
            name='category',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='assets.AssetType'),
        ),
        migrations.DeleteModel(
            name='AssetCategory',
        ),
    ]
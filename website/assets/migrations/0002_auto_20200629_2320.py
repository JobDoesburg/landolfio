# Generated by Django 3.0.5 on 2020-06-29 21:20

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('assets', '0001_initial'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='assetcategory',
            options={'verbose_name': 'asset category', 'verbose_name_plural': 'asset categories'},
        ),
        migrations.AlterModelOptions(
            name='assettype',
            options={'verbose_name': 'asset type', 'verbose_name_plural': 'asset types'},
        ),
        migrations.AddField(
            model_name='asset',
            name='status',
            field=models.IntegerField(choices=[(0, 'Unknown')], default=0),
        ),
        migrations.AlterUniqueTogether(
            name='asset',
            unique_together={('number', 'category')},
        ),
        migrations.CreateModel(
            name='AssetMemo',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', models.DateTimeField(auto_created=True)),
                ('memo', models.TextField()),
                ('instrument', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='assets.Asset')),
            ],
            options={
                'verbose_name': 'memo',
                'verbose_name_plural': 'memos',
            },
        ),
        migrations.CreateModel(
            name='AssetEvent',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', models.DateTimeField(auto_created=True)),
                ('event_date', models.DateTimeField()),
                ('type', models.IntegerField(choices=[(0, 'Rental start')])),
                ('instrument', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='assets.Asset')),
            ],
            options={
                'verbose_name': 'event',
                'verbose_name_plural': 'events',
            },
        ),
    ]

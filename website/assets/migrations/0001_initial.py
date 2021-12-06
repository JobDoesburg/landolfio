# Generated by Django 3.2.9 on 2021-12-05 15:38

import django.core.validators
from django.db import migrations, models
import django.db.models.deletion
import re


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='AssetCategory',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=20)),
                ('name_singular', models.CharField(max_length=20, validators=[django.core.validators.RegexValidator(re.compile('^[-\\w]+\\Z'), 'Enter a valid “slug” consisting of Unicode letters, numbers, underscores, or hyphens.', 'invalid')])),
            ],
            options={
                'verbose_name': 'category',
                'verbose_name_plural': 'categories',
            },
        ),
        migrations.CreateModel(
            name='AssetLocationGroup',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=20)),
            ],
            options={
                'verbose_name': 'location group',
                'verbose_name_plural': 'location groups',
            },
        ),
        migrations.CreateModel(
            name='AssetSize',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=20)),
                ('categories', models.ManyToManyField(to='assets.AssetCategory')),
            ],
            options={
                'verbose_name': 'size',
                'verbose_name_plural': 'sizes',
            },
        ),
        migrations.CreateModel(
            name='AssetLocation',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=20)),
                ('location_group', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='assets.assetlocationgroup')),
            ],
            options={
                'verbose_name': 'location',
                'verbose_name_plural': 'locations',
            },
        ),
        migrations.CreateModel(
            name='Asset',
            fields=[
                ('number', models.CharField(max_length=10, primary_key=True, serialize=False, unique=True, validators=[django.core.validators.RegexValidator(re.compile('^[-\\w]+\\Z'), 'Enter a valid “slug” consisting of Unicode letters, numbers, underscores, or hyphens.', 'invalid')])),
                ('status', models.IntegerField(choices=[(0, 'Unknown'), (1, 'Placeholder reserved'), (2, 'To be delivered'), (3, 'Under review'), (4, 'Maintenance (in house)'), (5, 'Maintenance (external)'), (6, 'Available'), (7, 'Issued (unprocessed)'), (8, 'Issued (rental)'), (9, 'Issued (loan)'), (10, 'Amortized'), (11, 'Sold')], default=1)),
                ('collection', models.IntegerField(choices=[(0, 'Business'), (1, 'Private'), (2, 'Consignment')], default=0)),
                ('tax_status', models.IntegerField(choices=[(0, 'Margin'), (1, 'Taxable')], default=1)),
                ('retail_value', models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True)),
                ('category', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='assets.assetcategory')),
                ('location', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, to='assets.assetlocation')),
                ('size', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, to='assets.assetsize')),
            ],
            options={
                'verbose_name': 'asset',
                'verbose_name_plural': 'assets',
            },
        ),
    ]

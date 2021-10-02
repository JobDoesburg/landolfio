# Generated by Django 3.0.8 on 2020-08-07 19:25

import django.core.validators
from django.db import migrations, models
import re


class Migration(migrations.Migration):

    dependencies = [
        ('assets', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='asset',
            name='number',
            field=models.CharField(max_length=10, primary_key=True, serialize=False, unique=True, validators=[django.core.validators.RegexValidator(re.compile('^[-\\w]+\\Z'), 'Enter a valid “slug” consisting of Unicode letters, numbers, underscores, or hyphens.', 'invalid')]),
        ),
    ]
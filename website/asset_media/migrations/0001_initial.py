# Generated by Django 3.0.8 on 2020-08-07 19:13

import asset_media.models
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('asset_events', '0001_initial'),
        ('assets', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='MediaSet',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.DateTimeField(default=django.utils.timezone.now)),
                ('remarks', models.TextField(blank=True, null=True)),
                ('asset', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='assets.Asset')),
                ('event', models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='asset_events.Event')),
            ],
            options={
                'verbose_name': 'media set',
                'verbose_name_plural': 'media sets',
            },
        ),
        migrations.CreateModel(
            name='MediaItem',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('media', models.FileField(upload_to=asset_media.models.get_upload_path)),
                ('set', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='media.MediaSet')),
            ],
            options={
                'verbose_name': 'media item',
                'verbose_name_plural': 'media items',
            },
        ),
    ]

# Generated by Django 3.0.8 on 2020-08-07 19:13

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('moneybird', '0001_initial'),
        ('assets', '0001_initial'),
        ('asset_events', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='AssetLoan',
            fields=[
                ('multiassetevent_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='asset_events.MultiAssetEvent')),
            ],
            options={
                'verbose_name': 'loan',
                'verbose_name_plural': 'loans',
            },
            bases=('asset_events.multiassetevent',),
        ),
        migrations.CreateModel(
            name='AssetRental',
            fields=[
                ('multiassetevent_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='asset_events.MultiAssetEvent')),
            ],
            options={
                'verbose_name': 'rental',
                'verbose_name_plural': 'rentals',
            },
            bases=('asset_events.multiassetevent',),
        ),
        migrations.CreateModel(
            name='AssetReturnal',
            fields=[
                ('multiassetevent_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='asset_events.MultiAssetEvent')),
            ],
            options={
                'verbose_name': 'returnal',
                'verbose_name_plural': 'returnals',
            },
            bases=('asset_events.multiassetevent',),
        ),
        migrations.CreateModel(
            name='SingleUnprocessedAssetIssuance',
            fields=[
                ('event_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='asset_events.Event')),
            ],
            options={
                'verbose_name': 'unprocessed asset issuance',
                'verbose_name_plural': 'unprocessed asset issuances',
            },
            bases=('asset_events.event',),
        ),
        migrations.CreateModel(
            name='LoanedAsset',
            fields=[
            ],
            options={
                'verbose_name': 'loaned asset',
                'verbose_name_plural': 'loaned assets',
                'proxy': True,
                'indexes': [],
                'constraints': [],
            },
            bases=('assets.asset',),
        ),
        migrations.CreateModel(
            name='RentAsset',
            fields=[
            ],
            options={
                'verbose_name': 'rented asset',
                'verbose_name_plural': 'rented assets',
                'proxy': True,
                'indexes': [],
                'constraints': [],
            },
            bases=('assets.asset',),
        ),
        migrations.CreateModel(
            name='UnprocessedIssuedAsset',
            fields=[
            ],
            options={
                'verbose_name': 'issued asset (unprocessed)',
                'verbose_name_plural': 'issued assets (unprocessed)',
                'proxy': True,
                'indexes': [],
                'constraints': [],
            },
            bases=('assets.asset',),
        ),
        migrations.CreateModel(
            name='UnprocessedAssetIssuance',
            fields=[
                ('multiassetevent_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='asset_events.MultiAssetEvent')),
                ('assets', models.ManyToManyField(through='rentals.SingleUnprocessedAssetIssuance', to='assets.Asset')),
                ('contact', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, to='moneybird.Contact')),
            ],
            options={
                'verbose_name': 'unprocessed issuance',
                'verbose_name_plural': 'unprocessed issuances',
            },
            bases=('asset_events.multiassetevent',),
        ),
        migrations.AddField(
            model_name='singleunprocessedassetissuance',
            name='issuance',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='rentals.UnprocessedAssetIssuance'),
        ),
        migrations.CreateModel(
            name='SingleAssetReturnal',
            fields=[
                ('event_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='asset_events.Event')),
                ('returnal', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='rentals.AssetReturnal')),
            ],
            options={
                'verbose_name': 'asset returnal',
                'verbose_name_plural': 'asset returnals',
            },
            bases=('asset_events.event',),
        ),
        migrations.CreateModel(
            name='SingleAssetRental',
            fields=[
                ('event_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='asset_events.Event')),
                ('rental', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='rentals.AssetRental')),
            ],
            options={
                'verbose_name': 'asset rental',
                'verbose_name_plural': 'asset rentals',
            },
            bases=('asset_events.event',),
        ),
        migrations.CreateModel(
            name='SingleAssetLoan',
            fields=[
                ('event_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='asset_events.Event')),
                ('loan', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='rentals.AssetLoan')),
            ],
            options={
                'verbose_name': 'asset loan',
                'verbose_name_plural': 'asset loans',
            },
            bases=('asset_events.event',),
        ),
        migrations.AddField(
            model_name='assetreturnal',
            name='assets',
            field=models.ManyToManyField(through='rentals.SingleAssetReturnal', to='assets.Asset'),
        ),
        migrations.AddField(
            model_name='assetrental',
            name='assets',
            field=models.ManyToManyField(through='rentals.SingleAssetRental', to='assets.Asset'),
        ),
        migrations.AddField(
            model_name='assetrental',
            name='contact',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, to='moneybird.Contact'),
        ),
        migrations.AddField(
            model_name='assetloan',
            name='assets',
            field=models.ManyToManyField(through='rentals.SingleAssetLoan', to='assets.Asset'),
        ),
        migrations.AddField(
            model_name='assetloan',
            name='contact',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, to='moneybird.Contact'),
        ),
    ]

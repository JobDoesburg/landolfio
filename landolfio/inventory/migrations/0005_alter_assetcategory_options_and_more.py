# Generated by Django 4.0.6 on 2022-08-02 07:12

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("inventory", "0004_remove_asset_remarks_alter_remark_asset"),
    ]

    operations = [
        migrations.AlterModelOptions(
            name="assetcategory",
            options={
                "ordering": ["order", "pk"],
                "verbose_name": "category",
                "verbose_name_plural": "categories",
            },
        ),
        migrations.AlterModelOptions(
            name="assetlocation",
            options={
                "ordering": ["location_group__order", "order", "pk"],
                "verbose_name": "location",
                "verbose_name_plural": "locations",
            },
        ),
        migrations.AlterModelOptions(
            name="assetlocationgroup",
            options={
                "ordering": ["order", "pk"],
                "verbose_name": "location group",
                "verbose_name_plural": "location groups",
            },
        ),
        migrations.AlterModelOptions(
            name="assetsize",
            options={
                "ordering": ["order", "pk"],
                "verbose_name": "size",
                "verbose_name_plural": "sizes",
            },
        ),
        migrations.AlterModelOptions(
            name="collection",
            options={"ordering": ["order", "pk"], "verbose_name": "Collectie"},
        ),
        migrations.AddField(
            model_name="assetcategory",
            name="order",
            field=models.PositiveSmallIntegerField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name="assetlocation",
            name="order",
            field=models.PositiveSmallIntegerField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name="assetlocationgroup",
            name="order",
            field=models.PositiveSmallIntegerField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name="assetsize",
            name="order",
            field=models.PositiveSmallIntegerField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name="collection",
            name="order",
            field=models.PositiveSmallIntegerField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name="attachment",
            name="asset",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="attachments",
                to="inventory.asset",
                verbose_name="Asset",
            ),
        ),
    ]

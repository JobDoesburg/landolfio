# Generated by Django 4.0.6 on 2022-08-05 10:44

import django.core.validators
from django.db import migrations, models
import django.db.models.deletion
import inventory.models.attachment
import re


class Migration(migrations.Migration):

    dependencies = [
        (
            "accounting",
            "0018_alter_contact_options_alter_documentstyle_options_and_more",
        ),
        ("inventory", "0005_alter_assetcategory_options_and_more"),
    ]

    operations = [
        migrations.AlterModelOptions(
            name="asset",
            options={
                "ordering": ["-created_at", "id"],
                "verbose_name": "asset",
                "verbose_name_plural": "assets",
            },
        ),
        migrations.AlterModelOptions(
            name="assetonestimatedocumentline",
            options={
                "verbose_name": "asset on estimate document line",
                "verbose_name_plural": "assets on estimate document lines",
            },
        ),
        migrations.AlterModelOptions(
            name="assetonjournaldocumentline",
            options={
                "verbose_name": "asset on journal document line",
                "verbose_name_plural": "assets on journal document lines",
            },
        ),
        migrations.AlterModelOptions(
            name="assetonrecurringsalesinvoicedocumentline",
            options={
                "verbose_name": "asset on recurring sales invoice document line",
                "verbose_name_plural": "assets on recurring sales invoice document lines",
            },
        ),
        migrations.AlterModelOptions(
            name="assetsubscription",
            options={
                "verbose_name": "asset subscription",
                "verbose_name_plural": "assets subscriptions",
            },
        ),
        migrations.AlterModelOptions(
            name="attachment",
            options={
                "ordering": ["upload_date"],
                "verbose_name": "attachment",
                "verbose_name_plural": "attachments",
            },
        ),
        migrations.AlterModelOptions(
            name="collection",
            options={
                "ordering": ["order", "pk"],
                "verbose_name": "collection",
                "verbose_name_plural": "collections",
            },
        ),
        migrations.AlterModelOptions(
            name="remark",
            options={"verbose_name": "remark", "verbose_name_plural": "remarks"},
        ),
        migrations.AlterField(
            model_name="asset",
            name="category",
            field=models.ForeignKey(
                null=True,
                on_delete=django.db.models.deletion.PROTECT,
                to="inventory.assetcategory",
                verbose_name="category",
            ),
        ),
        migrations.AlterField(
            model_name="asset",
            name="collection",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                to="inventory.collection",
                verbose_name="collection",
            ),
        ),
        migrations.AlterField(
            model_name="asset",
            name="created_at",
            field=models.DateTimeField(auto_now_add=True, verbose_name="created at"),
        ),
        migrations.AlterField(
            model_name="asset",
            name="estimate_document_lines",
            field=models.ManyToManyField(
                through="inventory.AssetOnEstimateDocumentLine",
                to="accounting.estimatedocumentline",
                verbose_name="estimate document lines",
            ),
        ),
        migrations.AlterField(
            model_name="asset",
            name="journal_document_lines",
            field=models.ManyToManyField(
                through="inventory.AssetOnJournalDocumentLine",
                to="accounting.journaldocumentline",
                verbose_name="journal document lines",
            ),
        ),
        migrations.AlterField(
            model_name="asset",
            name="listing_price",
            field=models.DecimalField(
                blank=True,
                decimal_places=2,
                max_digits=10,
                null=True,
                verbose_name="listing price",
            ),
        ),
        migrations.AlterField(
            model_name="asset",
            name="local_status",
            field=models.CharField(
                choices=[
                    ("unknown", "unknown"),
                    ("placeholder", "placeholder"),
                    ("to_be_delivered", "to be delivered"),
                    ("under_review", "under review"),
                    ("maintenance_in_house", "maintenance in house"),
                    ("maintenance_external", "maintenance external"),
                    ("available", "available"),
                    ("issued_unprocessed", "issued unprocessed"),
                    ("issued_rent", "issued rent"),
                    ("issued_loan", "issued loan"),
                    ("amortized", "amortized"),
                    ("sold", "sold"),
                ],
                default="unknown",
                max_length=40,
                verbose_name="local status",
            ),
        ),
        migrations.AlterField(
            model_name="asset",
            name="location",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.PROTECT,
                to="inventory.assetlocation",
                verbose_name="location",
            ),
        ),
        migrations.AlterField(
            model_name="asset",
            name="recurring_sales_invoice_document_lines",
            field=models.ManyToManyField(
                through="inventory.AssetOnRecurringSalesInvoiceDocumentLine",
                to="accounting.recurringsalesinvoicedocumentline",
                verbose_name="recurring sales invoice document lines",
            ),
        ),
        migrations.AlterField(
            model_name="asset",
            name="size",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.PROTECT,
                to="inventory.assetsize",
                verbose_name="size",
            ),
        ),
        migrations.AlterField(
            model_name="assetcategory",
            name="name",
            field=models.CharField(max_length=20, verbose_name="name"),
        ),
        migrations.AlterField(
            model_name="assetcategory",
            name="name_singular",
            field=models.CharField(
                max_length=20,
                validators=[
                    django.core.validators.RegexValidator(
                        re.compile("^[-\\w]+\\Z"),
                        "Enter a valid “slug” consisting of Unicode letters, numbers, underscores, or hyphens.",
                        "invalid",
                    )
                ],
                verbose_name="name singular",
            ),
        ),
        migrations.AlterField(
            model_name="assetcategory",
            name="order",
            field=models.PositiveSmallIntegerField(
                blank=True, null=True, verbose_name="order"
            ),
        ),
        migrations.AlterField(
            model_name="assetlocation",
            name="location_group",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.PROTECT,
                to="inventory.assetlocationgroup",
                verbose_name="location group",
            ),
        ),
        migrations.AlterField(
            model_name="assetlocation",
            name="name",
            field=models.CharField(max_length=20, verbose_name="name"),
        ),
        migrations.AlterField(
            model_name="assetlocation",
            name="order",
            field=models.PositiveSmallIntegerField(
                blank=True, null=True, verbose_name="order"
            ),
        ),
        migrations.AlterField(
            model_name="assetlocationgroup",
            name="name",
            field=models.CharField(max_length=20, verbose_name="name"),
        ),
        migrations.AlterField(
            model_name="assetlocationgroup",
            name="order",
            field=models.PositiveSmallIntegerField(
                blank=True, null=True, verbose_name="order"
            ),
        ),
        migrations.AlterField(
            model_name="assetonestimatedocumentline",
            name="asset",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="estimate_document_line_assets",
                to="inventory.asset",
                verbose_name="asset",
            ),
        ),
        migrations.AlterField(
            model_name="assetonestimatedocumentline",
            name="document_line",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="assets",
                to="accounting.estimatedocumentline",
                verbose_name="document line",
            ),
        ),
        migrations.AlterField(
            model_name="assetonestimatedocumentline",
            name="value",
            field=models.DecimalField(
                decimal_places=2, max_digits=10, verbose_name="value"
            ),
        ),
        migrations.AlterField(
            model_name="assetonjournaldocumentline",
            name="asset",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="journal_document_line_assets",
                to="inventory.asset",
                verbose_name="asset",
            ),
        ),
        migrations.AlterField(
            model_name="assetonjournaldocumentline",
            name="document_line",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="assets",
                to="accounting.journaldocumentline",
                verbose_name="document line",
            ),
        ),
        migrations.AlterField(
            model_name="assetonjournaldocumentline",
            name="value",
            field=models.DecimalField(
                decimal_places=2, max_digits=10, verbose_name="value"
            ),
        ),
        migrations.AlterField(
            model_name="assetonrecurringsalesinvoicedocumentline",
            name="asset",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="recurring_sales_invoice_document_line_assets",
                to="inventory.asset",
                verbose_name="asset",
            ),
        ),
        migrations.AlterField(
            model_name="assetonrecurringsalesinvoicedocumentline",
            name="document_line",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="assets",
                to="accounting.recurringsalesinvoicedocumentline",
                verbose_name="document line",
            ),
        ),
        migrations.AlterField(
            model_name="assetonrecurringsalesinvoicedocumentline",
            name="value",
            field=models.DecimalField(
                decimal_places=2, max_digits=10, verbose_name="value"
            ),
        ),
        migrations.AlterField(
            model_name="assetsize",
            name="categories",
            field=models.ManyToManyField(
                to="inventory.assetcategory", verbose_name="categories"
            ),
        ),
        migrations.AlterField(
            model_name="assetsize",
            name="name",
            field=models.CharField(max_length=20, verbose_name="name"),
        ),
        migrations.AlterField(
            model_name="assetsize",
            name="order",
            field=models.PositiveSmallIntegerField(
                blank=True, null=True, verbose_name="order"
            ),
        ),
        migrations.AlterField(
            model_name="assetsubscription",
            name="asset",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="asset_subscriptions",
                to="inventory.asset",
                verbose_name="asset",
            ),
        ),
        migrations.AlterField(
            model_name="assetsubscription",
            name="subscription",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="assets",
                to="accounting.subscription",
                verbose_name="subscription",
            ),
        ),
        migrations.AlterField(
            model_name="assetsubscription",
            name="value",
            field=models.DecimalField(
                decimal_places=2, max_digits=10, verbose_name="value"
            ),
        ),
        migrations.AlterField(
            model_name="attachment",
            name="asset",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="attachments",
                to="inventory.asset",
                verbose_name="asset",
            ),
        ),
        migrations.AlterField(
            model_name="attachment",
            name="attachment",
            field=models.FileField(
                upload_to=inventory.models.attachment.attachments_directory_path,
                verbose_name="attachment",
            ),
        ),
        migrations.AlterField(
            model_name="attachment",
            name="upload_date",
            field=models.DateField(auto_now_add=True, verbose_name="upload date"),
        ),
        migrations.AlterField(
            model_name="collection",
            name="commerce",
            field=models.BooleanField(default=True, verbose_name="commerce"),
        ),
        migrations.AlterField(
            model_name="collection",
            name="name",
            field=models.CharField(max_length=200, unique=True, verbose_name="name"),
        ),
        migrations.AlterField(
            model_name="collection",
            name="order",
            field=models.PositiveSmallIntegerField(
                blank=True, null=True, verbose_name="order"
            ),
        ),
        migrations.AlterField(
            model_name="remark",
            name="asset",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="remarks",
                to="inventory.asset",
                verbose_name="asset",
            ),
        ),
        migrations.AlterField(
            model_name="remark",
            name="remark",
            field=models.TextField(verbose_name="remark"),
        ),
    ]

# Generated by Django 4.0.6 on 2022-07-06 14:39

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ("inventory", "0004_assetcategory_assetlocationgroup_and_more"),
    ]

    operations = [
        migrations.CreateModel(
            name="Contact",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "moneybird_id",
                    models.PositiveBigIntegerField(
                        blank=True, null=True, verbose_name="Moneybird ID"
                    ),
                ),
                (
                    "moneybird_version",
                    models.PositiveBigIntegerField(
                        blank=True, null=True, verbose_name="Moneybird version"
                    ),
                ),
                (
                    "moneybird_json",
                    models.JSONField(null=True, verbose_name="JSON MoneyBird"),
                ),
                (
                    "company_name",
                    models.CharField(
                        blank=True,
                        max_length=100,
                        null=True,
                        verbose_name="company name",
                    ),
                ),
                (
                    "first_name",
                    models.CharField(
                        blank=True, max_length=100, null=True, verbose_name="voornaam"
                    ),
                ),
                (
                    "last_name",
                    models.CharField(
                        blank=True, max_length=100, null=True, verbose_name="achternaam"
                    ),
                ),
                (
                    "email",
                    models.EmailField(
                        blank=True, max_length=254, null=True, verbose_name="email"
                    ),
                ),
                (
                    "sepa_active",
                    models.BooleanField(default=False, verbose_name="sepa active"),
                ),
            ],
            options={
                "abstract": False,
            },
        ),
        migrations.CreateModel(
            name="Estimate",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "moneybird_id",
                    models.PositiveBigIntegerField(
                        blank=True, null=True, verbose_name="Moneybird ID"
                    ),
                ),
                (
                    "moneybird_json",
                    models.JSONField(null=True, verbose_name="JSON MoneyBird"),
                ),
                ("date", models.DateField()),
                (
                    "contact",
                    models.ForeignKey(
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="estimates",
                        to="accounting.contact",
                        verbose_name="Contact",
                    ),
                ),
            ],
            options={
                "abstract": False,
            },
        ),
        migrations.CreateModel(
            name="JournalDocument",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "moneybird_id",
                    models.PositiveBigIntegerField(
                        blank=True, null=True, verbose_name="Moneybird ID"
                    ),
                ),
                (
                    "moneybird_version",
                    models.PositiveBigIntegerField(
                        blank=True, null=True, verbose_name="Moneybird version"
                    ),
                ),
                ("date", models.DateField()),
                (
                    "moneybird_json",
                    models.JSONField(null=True, verbose_name="JSON MoneyBird"),
                ),
                (
                    "document_kind",
                    models.CharField(
                        choices=[
                            ("FAC", "Sales invoice"),
                            ("INK", "Purchase invoice"),
                            ("BON", "Bon"),
                            ("MEM", "General journal document"),
                        ],
                        max_length=3,
                        verbose_name="document kind",
                    ),
                ),
                (
                    "contact",
                    models.ForeignKey(
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="journal_documents",
                        to="accounting.contact",
                        verbose_name="Contact",
                    ),
                ),
            ],
            options={
                "verbose_name_plural": "Documenten",
                "ordering": ("date",),
                "unique_together": {("moneybird_id", "document_kind")},
            },
        ),
        migrations.CreateModel(
            name="Ledger",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "moneybird_id",
                    models.PositiveBigIntegerField(
                        blank=True, null=True, verbose_name="Moneybird ID"
                    ),
                ),
                ("name", models.CharField(blank=True, max_length=100, null=True)),
                (
                    "account_type",
                    models.CharField(
                        choices=[
                            ("non_current_assets", "non current assets"),
                            ("current_assets", "current assets"),
                            ("equity", "equity"),
                            ("provisions", "provisions"),
                            ("non_current_liabilities", "non current liabilities"),
                            ("current_liabilities", "current liabilities"),
                            ("revenue", "revenue"),
                            ("direct_costs", "direct costs"),
                            ("expenses", "expenses"),
                            ("other_income_expenses", "other income expenses"),
                        ],
                        max_length=100,
                        null=True,
                        verbose_name="Account type",
                    ),
                ),
                (
                    "ledger_kind",
                    models.CharField(
                        choices=[
                            ("VOORRAAD_MARGE", "Voorraad Marge"),
                            ("VOORRAAD_NIET_MARGE", "Voorraad niet-marge"),
                            (
                                "VOORRAAD_BIJ_VERKOOP_MARGE",
                                "Voorraadwaarde bij verkoop marge",
                            ),
                            (
                                "VOORRAAD_BIJ_VERKOOP_NIET_MARGE",
                                "Voorraadwaarde bij verkoop niet-marge",
                            ),
                            ("VERKOOP_MARGE", "Verkoop marge"),
                            ("VERKOOP_NIET_MARGE", "Verkoop niet-marge"),
                            ("DIRECTE_AFSCHRIJVING", "Directe afschrijving"),
                            ("AFSCHRIJVINGEN", "Afschrijvingen"),
                            ("BORGEN", "Borgen"),
                        ],
                        max_length=100,
                        null=True,
                        unique=True,
                        verbose_name="Soort",
                    ),
                ),
            ],
            options={
                "verbose_name": "Ledger account",
                "verbose_name_plural": "Ledger accounts",
            },
        ),
        migrations.CreateModel(
            name="Product",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "moneybird_id",
                    models.PositiveBigIntegerField(
                        blank=True, null=True, verbose_name="Moneybird ID"
                    ),
                ),
                (
                    "moneybird_json",
                    models.JSONField(null=True, verbose_name="JSON MoneyBird"),
                ),
            ],
            options={
                "abstract": False,
            },
        ),
        migrations.CreateModel(
            name="Subscription",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "moneybird_id",
                    models.PositiveBigIntegerField(
                        blank=True, null=True, verbose_name="Moneybird ID"
                    ),
                ),
                (
                    "moneybird_json",
                    models.JSONField(null=True, verbose_name="JSON MoneyBird"),
                ),
            ],
            options={
                "abstract": False,
            },
        ),
        migrations.CreateModel(
            name="JournalDocumentLine",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "moneybird_id",
                    models.PositiveBigIntegerField(
                        blank=True, null=True, verbose_name="Moneybird ID"
                    ),
                ),
                (
                    "moneybird_json",
                    models.JSONField(null=True, verbose_name="JSON MoneyBird"),
                ),
                (
                    "price",
                    models.DecimalField(
                        decimal_places=4, max_digits=19, verbose_name="Prijs"
                    ),
                ),
                (
                    "asset_id_field",
                    models.CharField(max_length=50, null=True, verbose_name="Asset-ID"),
                ),
                (
                    "asset",
                    models.ForeignKey(
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="document_lines",
                        to="inventory.asset",
                        verbose_name="Asset",
                    ),
                ),
                (
                    "document",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="document_lines",
                        to="accounting.journaldocument",
                        verbose_name="Document",
                    ),
                ),
                (
                    "ledger",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT,
                        to="accounting.ledger",
                        verbose_name="Grootboekrekening",
                    ),
                ),
            ],
            options={
                "verbose_name": "Documentregel",
                "ordering": ("document__date",),
            },
        ),
        migrations.CreateModel(
            name="EstimateDocumentLine",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "moneybird_id",
                    models.PositiveBigIntegerField(
                        blank=True, null=True, verbose_name="Moneybird ID"
                    ),
                ),
                (
                    "moneybird_json",
                    models.JSONField(null=True, verbose_name="JSON MoneyBird"),
                ),
                (
                    "asset_id_field",
                    models.CharField(max_length=50, null=True, verbose_name="Asset-ID"),
                ),
                (
                    "asset",
                    models.ForeignKey(
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="estimate_document_lines",
                        to="inventory.asset",
                        verbose_name="Asset",
                    ),
                ),
                (
                    "document",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="document_lines",
                        to="accounting.estimate",
                        verbose_name="Document",
                    ),
                ),
            ],
            options={
                "verbose_name": "Documentregel",
                "ordering": ("document__date",),
            },
        ),
    ]

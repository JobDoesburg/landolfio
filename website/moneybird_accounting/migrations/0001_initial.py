# Generated by Django 3.0.8 on 2020-07-24 13:20

from django.db import migrations, models
import django.db.models.deletion
import django_countries.fields
import django_iban.fields


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Contact',
            fields=[
                ('id', models.CharField(editable=False, help_text='This is the primary key of this object, both for this application and in Moneybird.', max_length=20, primary_key=True, serialize=False)),
                ('version', models.IntegerField(blank=True, help_text='This is the Moneybird version of the currently stored data and is used when looking for changes efficiently.', null=True, unique=True)),
                ('company_name', models.CharField(blank=True, max_length=100, null=True)),
                ('firstname', models.CharField(blank=True, max_length=100, null=True)),
                ('lastname', models.CharField(blank=True, max_length=100, null=True)),
                ('address1', models.CharField(blank=True, max_length=100, null=True)),
                ('address2', models.CharField(blank=True, max_length=100, null=True)),
                ('zipcode', models.CharField(blank=True, max_length=10, null=True)),
                ('city', models.CharField(blank=True, max_length=100, null=True)),
                ('country', django_countries.fields.CountryField(blank=True, help_text='Will be automatically set to the standard Moneybird administration country if empty.', max_length=2, null=True)),
                ('phone', models.CharField(blank=True, max_length=100, null=True)),
                ('delivery_method', models.CharField(blank=True, choices=[('Email', 'Email'), ('Simplerinvoicing', 'Simplerinvoicing'), ('Post', 'Post'), ('Manual', 'Manual')], default='Email', max_length=16, null=True)),
                ('customer_id', models.IntegerField(blank=True, help_text='Will be assigned automatically if empty. Should be unique for the administration.', null=True)),
                ('tax_number', models.CharField(blank=True, max_length=100, null=True)),
                ('chamber_of_commerce', models.CharField(blank=True, max_length=100, null=True)),
                ('bank_account', models.CharField(blank=True, max_length=100, null=True)),
                ('attention', models.CharField(blank=True, max_length=100, null=True)),
                ('email', models.CharField(blank=True, max_length=200, null=True)),
                ('email_ubl', models.BooleanField(blank=True, null=True)),
                ('send_invoices_to_attention', models.CharField(blank=True, max_length=100, null=True)),
                ('send_invoices_to_email', models.CharField(blank=True, help_text='Can be a single email or a comma-separated list of emails', max_length=200, null=True)),
                ('send_estimates_to_attention', models.CharField(blank=True, max_length=100, null=True)),
                ('send_estimates_to_email', models.CharField(blank=True, help_text='Can be a single email or a comma-separated list of emails', max_length=200, null=True)),
                ('sepa_active', models.BooleanField(default=False, help_text='When true, all SEPA fields are required.')),
                ('sepa_iban', django_iban.fields.IBANField(blank=True, enforce_database_constraint=True, max_length=100, null=True)),
                ('sepa_iban_account_name', models.CharField(blank=True, max_length=100, null=True)),
                ('sepa_bic', models.CharField(blank=True, max_length=100, null=True)),
                ('sepa_mandate_id', models.CharField(blank=True, max_length=100, null=True)),
                ('sepa_mandate_date', models.DateField(blank=True, help_text='Should be a date in the past.', null=True)),
                ('sepa_sequence_type', models.CharField(blank=True, choices=[('RCUR', 'RCUR'), ('FRST', 'FRST'), ('OOFF', 'OOFF'), ('FNAL', 'FNAL')], max_length=4, null=True)),
            ],
            options={
                'verbose_name': 'contact',
                'verbose_name_plural': 'contacts',
            },
        ),
        migrations.CreateModel(
            name='LedgerAccount',
            fields=[
                ('id', models.CharField(editable=False, help_text='This is the primary key of this object, both for this application and in Moneybird.', max_length=20, primary_key=True, serialize=False)),
                ('name', models.CharField(blank=True, max_length=100, null=True)),
                ('account_type', models.CharField(blank=True, choices=[('non_current_assets', 'Non-current assets'), ('current_assets', 'Currents assets'), ('equity', 'Equity'), ('provisions', 'Provisions'), ('non_current_liabilities', 'Non-current liabilities'), ('current_liabilities', 'Current liabilities'), ('revenue', 'Revenue'), ('direct_costs', 'Direct costs'), ('expenses', 'Expenses'), ('other_income_expenses', 'Other income or expenses')], max_length=50, null=True)),
                ('account_id', models.CharField(blank=True, max_length=10, null=True)),
                ('parent', models.ForeignKey(blank=True, db_constraint=False, null=True, on_delete=django.db.models.deletion.PROTECT, to='moneybird.LedgerAccount')),
            ],
            options={
                'verbose_name': 'ledger account',
                'verbose_name_plural': 'ledger accounts',
            },
        ),
        migrations.CreateModel(
            name='Product',
            fields=[
                ('id', models.CharField(editable=False, help_text='This is the primary key of this object, both for this application and in Moneybird.', max_length=20, primary_key=True, serialize=False)),
                ('description', models.CharField(blank=True, max_length=1000, null=True)),
                ('price', models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True)),
                ('ledger_account', models.ForeignKey(blank=True, db_constraint=False, null=True, on_delete=django.db.models.deletion.PROTECT, to='moneybird.LedgerAccount')),
            ],
            options={
                'verbose_name': 'product',
                'verbose_name_plural': 'products',
            },
        ),
        migrations.CreateModel(
            name='Project',
            fields=[
                ('id', models.CharField(editable=False, help_text='This is the primary key of this object, both for this application and in Moneybird.', max_length=20, primary_key=True, serialize=False)),
                ('name', models.CharField(blank=True, max_length=100, null=True)),
                ('state', models.CharField(blank=True, choices=[('active', 'Active'), ('archived', 'Archived')], max_length=10, null=True)),
            ],
            options={
                'verbose_name': 'project',
                'verbose_name_plural': 'projects',
            },
        ),
        migrations.CreateModel(
            name='TaxRate',
            fields=[
                ('id', models.CharField(editable=False, help_text='This is the primary key of this object, both for this application and in Moneybird.', max_length=20, primary_key=True, serialize=False)),
                ('name', models.CharField(blank=True, max_length=100, null=True)),
                ('percentage', models.DecimalField(blank=True, decimal_places=2, max_digits=5, null=True)),
                ('show_tax', models.BooleanField(blank=True, null=True)),
                ('active', models.BooleanField(blank=True, null=True)),
            ],
            options={
                'verbose_name': 'tax rate',
                'verbose_name_plural': 'tax rates',
            },
        ),
        migrations.CreateModel(
            name='Workflow',
            fields=[
                ('id', models.CharField(editable=False, help_text='This is the primary key of this object, both for this application and in Moneybird.', max_length=20, primary_key=True, serialize=False)),
                ('type', models.CharField(blank=True, choices=[('InvoiceWorkflow', 'Invoice Workflow'), ('EstimateWorkflow', 'Estimate Workflow')], max_length=20, null=True)),
                ('name', models.CharField(blank=True, max_length=100, null=True)),
                ('default', models.BooleanField(blank=True, null=True)),
                ('active', models.BooleanField(blank=True, null=True)),
                ('prices_are_incl_tax', models.BooleanField(blank=True, null=True)),
            ],
            options={
                'verbose_name': 'workflow',
                'verbose_name_plural': 'workflows',
            },
        ),
        migrations.CreateModel(
            name='SalesInvoice',
            fields=[
                ('id', models.CharField(editable=False, help_text='This is the primary key of this object, both for this application and in Moneybird.', max_length=20, primary_key=True, serialize=False)),
                ('version', models.IntegerField(blank=True, help_text='This is the Moneybird version of the currently stored data and is used when looking for changes efficiently.', null=True, unique=True)),
                ('invoice_id', models.CharField(blank=True, max_length=20, null=True, unique=True)),
                ('draft_id', models.CharField(blank=True, max_length=20, null=True, unique=True)),
                ('state', models.CharField(blank=True, choices=[('draft', 'Draft'), ('open', 'Open'), ('scheduled', 'Scheduled'), ('pending_payment', 'Pending payment'), ('late', 'Late'), ('reminded', 'Reminded'), ('paid', 'Paid'), ('uncollectible', 'Uncollectible')], max_length=100, null=True)),
                ('reference', models.CharField(blank=True, max_length=1000, null=True)),
                ('invoice_date', models.DateField(blank=True, help_text='Will be set automatically when invoice is sent.', null=True)),
                ('first_due_interval', models.IntegerField(blank=True, null=True)),
                ('due_date', models.DateField(blank=True, null=True)),
                ('discount', models.DecimalField(blank=True, decimal_places=2, max_digits=5, null=True)),
                ('paused', models.BooleanField(default=False)),
                ('paid_at', models.DateField(blank=True, null=True)),
                ('sent_at', models.DateField(blank=True, null=True)),
                ('payment_conditions', models.TextField(blank=True, help_text='Supports Moneybird tags in the form of {document.field}.', null=True)),
                ('payment_reference', models.CharField(blank=True, max_length=100, null=True)),
                ('public_view_code', models.CharField(blank=True, max_length=100, null=True)),
                ('url', models.CharField(blank=True, max_length=1000, null=True)),
                ('payment_url', models.CharField(blank=True, max_length=1000, null=True)),
                ('total_paid', models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True)),
                ('total_unpaid', models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True)),
                ('total_unpaid_base', models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True)),
                ('total_price_excl_tax', models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True)),
                ('total_price_excl_tax_base', models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True)),
                ('total_price_incl_tax', models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True)),
                ('total_price_incl_tax_base', models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True)),
                ('total_discount', models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True)),
                ('prices_are_incl_tax', models.BooleanField(default=True, verbose_name='display prices incl. tax')),
                ('contact', models.ForeignKey(db_constraint=False, on_delete=django.db.models.deletion.PROTECT, to='moneybird.Contact')),
                ('original_sales_invoice', models.ForeignKey(blank=True, db_constraint=False, null=True, on_delete=django.db.models.deletion.CASCADE, to='moneybird.SalesInvoice')),
                ('workflow', models.ForeignKey(blank=True, limit_choices_to={'type': 'InvoiceWorkflow'}, null=True, on_delete=django.db.models.deletion.PROTECT, to='moneybird.Workflow')),
            ],
            options={
                'verbose_name': 'sales invoice',
                'verbose_name_plural': 'sales invoices',
            },
        ),
        migrations.CreateModel(
            name='RecurringSalesInvoice',
            fields=[
                ('id', models.CharField(editable=False, help_text='This is the primary key of this object, both for this application and in Moneybird.', max_length=20, primary_key=True, serialize=False)),
                ('version', models.IntegerField(blank=True, help_text='This is the Moneybird version of the currently stored data and is used when looking for changes efficiently.', null=True, unique=True)),
                ('active', models.BooleanField(blank=True, null=True)),
                ('auto_send', models.BooleanField(blank=True, null=True)),
                ('mergeable', models.BooleanField(blank=True, null=True)),
                ('has_desired_count', models.BooleanField(blank=True, null=True)),
                ('desired_count', models.PositiveIntegerField(blank=True, null=True)),
                ('frequency', models.PositiveIntegerField(blank=True, null=True)),
                ('frequency_type', models.CharField(blank=True, choices=[('day', 'Daily'), ('week', 'Weekly'), ('month', 'Monthly'), ('quarter', 'Quarterly'), ('year', 'Annually')], max_length=20, null=True)),
                ('start_date', models.DateField(blank=True, null=True)),
                ('invoice_date', models.DateField(blank=True, null=True)),
                ('last_date', models.DateField(blank=True, null=True)),
                ('reference', models.CharField(blank=True, max_length=1000, null=True)),
                ('first_due_interval', models.IntegerField(blank=True, null=True)),
                ('discount', models.DecimalField(blank=True, decimal_places=2, max_digits=5, null=True)),
                ('payment_conditions', models.TextField(blank=True, help_text='Supports Moneybird tags in the form of {document.field}.', null=True)),
                ('total_price_excl_tax', models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True)),
                ('total_price_excl_tax_base', models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True)),
                ('total_price_incl_tax', models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True)),
                ('total_price_incl_tax_base', models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True)),
                ('total_discount', models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True)),
                ('prices_are_incl_tax', models.BooleanField(default=True, verbose_name='display prices incl. tax')),
                ('contact', models.ForeignKey(db_constraint=False, on_delete=django.db.models.deletion.PROTECT, to='moneybird.Contact')),
                ('workflow', models.ForeignKey(blank=True, limit_choices_to={'type': 'InvoiceWorkflow'}, null=True, on_delete=django.db.models.deletion.PROTECT, to='moneybird.Workflow')),
            ],
            options={
                'verbose_name': 'recurring sales invoice',
                'verbose_name_plural': 'recurring sales invoices',
            },
        ),
        migrations.CreateModel(
            name='RecurringInvoiceDetailItem',
            fields=[
                ('id', models.CharField(editable=False, help_text='This is the primary key of this object, both for this application and in Moneybird.', max_length=20, primary_key=True, serialize=False)),
                ('amount', models.CharField(blank=True, max_length=10, null=True)),
                ('amount_decimal', models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True)),
                ('description', models.CharField(blank=True, max_length=1000, null=True)),
                ('price', models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True)),
                ('period', models.CharField(blank=True, help_text="Allowed input format: yyyymmdd..yyyymmdd, OR 'this_month', 'prev_month', 'next_month'.", max_length=100, null=True)),
                ('row_order', models.PositiveSmallIntegerField(blank=True, null=True)),
                ('total_price_excl_tax_with_discount', models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True)),
                ('total_price_excl_tax_with_discount_base', models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True)),
                ('invoice', models.ForeignKey(db_constraint=False, on_delete=django.db.models.deletion.CASCADE, related_name='details', to='moneybird.RecurringSalesInvoice')),
                ('ledger_account', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, to='moneybird.LedgerAccount')),
                ('product', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, to='moneybird.Product')),
                ('project', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, to='moneybird.Project')),
                ('tax_rate', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, to='moneybird.TaxRate')),
            ],
            options={
                'verbose_name': 'recurring sales invoice detail item',
                'verbose_name_plural': 'recurring sales invoice detail items',
            },
        ),
        migrations.AddField(
            model_name='product',
            name='tax_rate',
            field=models.ForeignKey(blank=True, db_constraint=False, null=True, on_delete=django.db.models.deletion.PROTECT, to='moneybird.TaxRate'),
        ),
        migrations.CreateModel(
            name='InvoiceDetailItem',
            fields=[
                ('id', models.CharField(editable=False, help_text='This is the primary key of this object, both for this application and in Moneybird.', max_length=20, primary_key=True, serialize=False)),
                ('amount', models.CharField(blank=True, max_length=10, null=True)),
                ('amount_decimal', models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True)),
                ('description', models.CharField(blank=True, max_length=1000, null=True)),
                ('price', models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True)),
                ('period', models.CharField(blank=True, help_text="Allowed input format: yyyymmdd..yyyymmdd, OR 'this_month', 'prev_month', 'next_month'.", max_length=100, null=True)),
                ('row_order', models.PositiveSmallIntegerField(blank=True, null=True)),
                ('total_price_excl_tax_with_discount', models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True)),
                ('total_price_excl_tax_with_discount_base', models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True)),
                ('invoice', models.ForeignKey(db_constraint=False, on_delete=django.db.models.deletion.CASCADE, related_name='details', to='moneybird.SalesInvoice')),
                ('ledger_account', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, to='moneybird.LedgerAccount')),
                ('product', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, to='moneybird.Product')),
                ('project', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, to='moneybird.Project')),
                ('tax_rate', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, to='moneybird.TaxRate')),
            ],
            options={
                'verbose_name': 'invoice detail item',
                'verbose_name_plural': 'invoice detail items',
            },
        ),
    ]

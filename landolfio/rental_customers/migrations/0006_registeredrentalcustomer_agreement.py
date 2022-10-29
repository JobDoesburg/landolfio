# Generated by Django 4.1.2 on 2022-10-28 21:53

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        (
            "accounting",
            "0020_alter_contact_options_alter_documentstyle_options_and_more",
        ),
        ("rental_customers", "0005_alter_registeredrentalcustomer_assets"),
    ]

    operations = [
        migrations.AddField(
            model_name="registeredrentalcustomer",
            name="agreement",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                to="accounting.estimate",
                verbose_name="agreement",
            ),
        ),
    ]

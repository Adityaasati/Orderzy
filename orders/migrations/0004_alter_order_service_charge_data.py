# Generated by Django 5.0.6 on 2024-06-20 15:55

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("orders", "0003_order_restaurant_order_total_data"),
    ]

    operations = [
        migrations.AlterField(
            model_name="order",
            name="service_charge_data",
            field=models.JSONField(
                blank=True,
                help_text="Data format: {'service_charge_type':{'service_charge_percentage':'service_charge_amount'}}",
                null=True,
            ),
        ),
    ]

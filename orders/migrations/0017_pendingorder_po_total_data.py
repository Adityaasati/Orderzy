# Generated by Django 5.0.6 on 2024-08-14 17:40

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("orders", "0016_remove_pendingorder_po_restaurant_ids_and_more"),
    ]

    operations = [
        migrations.AddField(
            model_name="pendingorder",
            name="po_total_data",
            field=models.JSONField(blank=True, null=True),
        ),
    ]

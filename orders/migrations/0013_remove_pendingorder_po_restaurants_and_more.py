# Generated by Django 5.0.6 on 2024-08-14 08:06

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("orders", "0012_pendingorder_po_restaurants"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="pendingorder",
            name="po_restaurants",
        ),
        migrations.AddField(
            model_name="pendingorder",
            name="po_restaurant_slug",
            field=models.SlugField(blank=True, max_length=100, null=True, unique=True),
        ),
    ]

# Generated by Django 5.0.6 on 2024-07-30 07:02

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("orders", "0009_alter_pendingorder_po_id"),
    ]

    operations = [
        migrations.RenameField(
            model_name="pendingorder",
            old_name="po_id",
            new_name="id",
        ),
    ]

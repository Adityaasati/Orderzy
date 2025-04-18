# Generated by Django 5.0.6 on 2024-07-30 06:56

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("orders", "0007_alter_pendingorder_preorder_time"),
    ]

    operations = [
        migrations.RenameField(
            model_name="pendingorder",
            old_name="created_at",
            new_name="po_created_at",
        ),
        migrations.RemoveField(
            model_name="order",
            name="address",
        ),
        migrations.RemoveField(
            model_name="order",
            name="city",
        ),
        migrations.RemoveField(
            model_name="order",
            name="country",
        ),
        migrations.RemoveField(
            model_name="order",
            name="pin_code",
        ),
        migrations.RemoveField(
            model_name="order",
            name="state",
        ),
        migrations.RemoveField(
            model_name="pendingorder",
            name="id",
        ),
        migrations.RemoveField(
            model_name="pendingorder",
            name="order",
        ),
        migrations.RemoveField(
            model_name="pendingorder",
            name="preorder_time",
        ),
        migrations.RemoveField(
            model_name="pendingorder",
            name="restaurant",
        ),
        migrations.RemoveField(
            model_name="pendingorder",
            name="scheduled_for",
        ),
        migrations.RemoveField(
            model_name="pendingorder",
            name="updated_at",
        ),
        migrations.AddField(
            model_name="order",
            name="pre_order_time",
            field=models.FloatField(default=0),
        ),
        migrations.AddField(
            model_name="pendingorder",
            name="original_order",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="pending_orders",
                to="orders.order",
            ),
        ),
        migrations.AddField(
            model_name="pendingorder",
            name="po_id",
            field=models.AutoField(primary_key=True, serialize=False),
        ),
        migrations.AddField(
            model_name="pendingorder",
            name="po_is_ordered",
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name="pendingorder",
            name="po_name",
            field=models.CharField(default="Unnamed Pending Order", max_length=50),
        ),
        migrations.AddField(
            model_name="pendingorder",
            name="po_order_number",
            field=models.CharField(default="N/A", max_length=20),
        ),
        migrations.AddField(
            model_name="pendingorder",
            name="po_ordered_food_details",
            field=models.JSONField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name="pendingorder",
            name="po_pre_order_time",
            field=models.FloatField(default=0),
        ),
        migrations.AddField(
            model_name="pendingorder",
            name="po_status",
            field=models.CharField(
                choices=[
                    ("New", "New"),
                    ("Accepted", "Accepted"),
                    ("Completed", "Completed"),
                    ("Cancelled", "Cancelled"),
                ],
                default="New",
                max_length=15,
            ),
        ),
        migrations.AddField(
            model_name="pendingorder",
            name="po_total",
            field=models.DecimalField(decimal_places=2, default=0.0, max_digits=10),
        ),
    ]

# Generated by Django 5.0.6 on 2024-09-29 12:55

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("restaurant", "0009_restaurant_menu_url"),
    ]

    operations = [
        migrations.AlterField(
            model_name="openinghour",
            name="from_hour",
            field=models.TimeField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name="openinghour",
            name="to_hour",
            field=models.TimeField(blank=True, null=True),
        ),
    ]

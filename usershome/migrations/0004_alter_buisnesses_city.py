# Generated by Django 5.1.4 on 2025-02-14 09:36

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("usershome", "0003_rename_area_name_locality_locality_name"),
    ]

    operations = [
        migrations.AlterField(
            model_name="buisnesses",
            name="city",
            field=models.ForeignKey(
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                to="usershome.city",
            ),
        ),
    ]

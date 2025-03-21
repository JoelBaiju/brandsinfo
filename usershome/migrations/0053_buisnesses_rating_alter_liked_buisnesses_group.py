# Generated by Django 5.1.4 on 2025-03-16 16:29

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("usershome", "0052_home_ads_banner"),
    ]

    operations = [
        migrations.AddField(
            model_name="buisnesses",
            name="rating",
            field=models.FloatField(default=0),
        ),
        migrations.AlterField(
            model_name="liked_buisnesses",
            name="group",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="liked_buisnesses",
                to="usershome.liked_buisnesses_group",
            ),
        ),
    ]

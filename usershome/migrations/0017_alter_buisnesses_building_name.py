# Generated by Django 5.2.1 on 2025-05-24 06:33

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('usershome', '0016_plans_verbouse_name'),
    ]

    operations = [
        migrations.AlterField(
            model_name='buisnesses',
            name='building_name',
            field=models.CharField(blank=True, max_length=2000, null=True),
        ),
    ]

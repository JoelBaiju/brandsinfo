# Generated by Django 5.2 on 2025-05-03 16:36

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('usershome', '0012_merge_20250426_1043'),
    ]

    operations = [
        migrations.AlterField(
            model_name='product_sub_category',
            name='general_cat',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='subcats', to='usershome.product_general_category'),
        ),
    ]

# Generated by Django 5.1.4 on 2025-02-19 10:14

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("usershome", "0005_alter_buisnesses_city"),
    ]

    operations = [
        migrations.AddField(
            model_name="buisnesses",
            name="score",
            field=models.CharField(blank=True, max_length=25, null=True),
        ),
    ]

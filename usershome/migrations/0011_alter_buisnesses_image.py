# Generated by Django 5.1.4 on 2025-02-19 12:32

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("usershome", "0010_alter_buisnesses_image"),
    ]

    operations = [
        migrations.AlterField(
            model_name="buisnesses",
            name="image",
            field=models.ImageField(default="", upload_to="Profile_pics/"),
        ),
    ]

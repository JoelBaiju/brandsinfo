# Generated by Django 5.1.4 on 2025-03-16 13:14

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("usershome", "0051_home_ads"),
    ]

    operations = [
        migrations.AddField(
            model_name="home_ads",
            name="banner",
            field=models.ImageField(
                blank=True, default="", null=True, upload_to="Home_Ad_Banners/"
            ),
        ),
    ]

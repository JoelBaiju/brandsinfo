# Generated by Django 5.1.4 on 2025-03-13 07:56

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("usershome", "0047_remove_reviews_ratings_image_review_pics"),
    ]

    operations = [
        migrations.AddField(
            model_name="buisnesses",
            name="assured",
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name="buisnesses",
            name="verified",
            field=models.BooleanField(default=False),
        ),
    ]

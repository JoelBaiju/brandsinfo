# Generated by Django 5.1.4 on 2025-03-11 13:33

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("usershome", "0031_keywords_remove_buisness_offers_offer_type_and_more"),
    ]

    operations = [
        migrations.AddField(
            model_name="sitemap_links",
            name="meta_author",
            field=models.CharField(max_length=400, null=True),
        ),
        migrations.AddField(
            model_name="sitemap_links",
            name="meta_description",
            field=models.CharField(max_length=400, null=True),
        ),
        migrations.AddField(
            model_name="sitemap_links",
            name="meta_keywords",
            field=models.CharField(max_length=400, null=True),
        ),
        migrations.AddField(
            model_name="sitemap_links",
            name="meta_title",
            field=models.CharField(max_length=400, null=True),
        ),
        migrations.AddField(
            model_name="sitemap_links",
            name="page_title",
            field=models.CharField(max_length=400, null=True),
        ),
    ]

# Generated by Django 5.2.3 on 2025-07-01 10:49

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('usershome', '0024_admindirecttransactions'),
    ]

    operations = [
        migrations.CreateModel(
            name='BuisnessYoutubeVideos',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('youtube_link', models.CharField(max_length=400, null=True)),
                ('business', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='youtube_videos', to='usershome.buisnesses')),
            ],
        ),
    ]

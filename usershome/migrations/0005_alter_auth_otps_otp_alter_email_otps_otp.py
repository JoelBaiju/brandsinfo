# Generated by Django 5.1.4 on 2025-04-17 10:01

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        (
            "usershome",
            "0004_remove_phonepetransaction_usershome_p_busines_a40b6a_idx_and_more",
        ),
    ]

    operations = [
        migrations.AlterField(
            model_name="auth_otps",
            name="otp",
            field=models.CharField(max_length=20),
        ),
        migrations.AlterField(
            model_name="email_otps",
            name="otp",
            field=models.CharField(max_length=20),
        ),
    ]

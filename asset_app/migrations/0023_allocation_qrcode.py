# Generated by Django 3.2.12 on 2022-04-18 21:18

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('asset_app', '0022_auto_20220416_1712'),
    ]

    operations = [
        migrations.AddField(
            model_name='allocation',
            name='qrcode',
            field=models.CharField(blank=True, max_length=255),
        ),
    ]
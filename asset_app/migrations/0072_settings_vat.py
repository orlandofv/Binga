# Generated by Django 3.2.12 on 2022-08-19 07:15

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('asset_app', '0071_auto_20220818_0146'),
    ]

    operations = [
        migrations.AddField(
            model_name='settings',
            name='vat',
            field=models.CharField(blank=True, max_length=15, verbose_name='VAT number'),
        ),
    ]

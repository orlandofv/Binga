# Generated by Django 3.2.12 on 2022-04-20 10:08

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('asset_app', '0031_alter_workorder_progress'),
    ]

    operations = [
        migrations.AlterField(
            model_name='workorder',
            name='progress',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=2, verbose_name='Work Progress (%)'),
        ),
    ]

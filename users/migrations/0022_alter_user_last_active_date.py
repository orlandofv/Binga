# Generated by Django 3.2.12 on 2022-08-28 11:16

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0021_alter_user_last_active_date'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='last_active_date',
            field=models.DateTimeField(blank=True, default=datetime.datetime(2023, 8, 28, 13, 16, 14, 827389), verbose_name='Última data ativa'),
        ),
    ]

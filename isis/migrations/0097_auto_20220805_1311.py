# Generated by Django 3.2.12 on 2022-08-05 11:11

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('isis', '0096_auto_20220805_1202'),
    ]

    operations = [
        migrations.AlterField(
            model_name='invoice',
            name='due_date',
            field=models.DateTimeField(default=datetime.datetime(2022, 9, 4, 13, 11, 23, 151158), verbose_name='Due Date'),
        ),
        migrations.AlterField(
            model_name='invoicing',
            name='due_date',
            field=models.DateTimeField(default=datetime.datetime(2022, 9, 4, 13, 11, 23, 121189), verbose_name='Due Date'),
        ),
    ]

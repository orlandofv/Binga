# Generated by Django 3.2.12 on 2022-08-14 12:31

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('isis', '0102_auto_20220812_0143'),
    ]

    operations = [
        migrations.AlterField(
            model_name='invoice',
            name='due_date',
            field=models.DateTimeField(default=datetime.datetime(2022, 9, 13, 14, 31, 3, 170902), verbose_name='Due Date'),
        ),
        migrations.AlterField(
            model_name='invoicing',
            name='due_date',
            field=models.DateTimeField(default=datetime.datetime(2022, 9, 13, 14, 31, 3, 166914), verbose_name='Due Date'),
        ),
    ]

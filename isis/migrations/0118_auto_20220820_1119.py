# Generated by Django 3.2.12 on 2022-08-20 09:19

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('isis', '0117_auto_20220820_1111'),
    ]

    operations = [
        migrations.AlterField(
            model_name='invoice',
            name='due_date',
            field=models.DateTimeField(default=datetime.datetime(2022, 9, 19, 11, 19, 12, 892893), verbose_name='Due Date'),
        ),
        migrations.AlterField(
            model_name='invoicing',
            name='due_date',
            field=models.DateTimeField(default=datetime.datetime(2022, 9, 19, 11, 19, 12, 888867), verbose_name='Due Date'),
        ),
    ]

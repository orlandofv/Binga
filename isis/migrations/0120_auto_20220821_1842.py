# Generated by Django 3.2.12 on 2022-08-21 16:42

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('isis', '0119_auto_20220821_1825'),
    ]

    operations = [
        migrations.AlterField(
            model_name='invoice',
            name='due_date',
            field=models.DateTimeField(default=datetime.datetime(2022, 9, 20, 18, 42, 15, 418923), verbose_name='Due Date'),
        ),
        migrations.AlterField(
            model_name='invoicing',
            name='due_date',
            field=models.DateTimeField(default=datetime.datetime(2022, 9, 20, 18, 42, 15, 418923), verbose_name='Due Date'),
        ),
    ]
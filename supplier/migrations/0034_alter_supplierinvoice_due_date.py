# Generated by Django 3.2.12 on 2022-08-15 07:13

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('supplier', '0033_alter_supplierinvoice_due_date'),
    ]

    operations = [
        migrations.AlterField(
            model_name='supplierinvoice',
            name='due_date',
            field=models.DateTimeField(default=datetime.datetime(2022, 9, 14, 9, 13, 48, 583038), verbose_name='Due Date'),
        ),
    ]

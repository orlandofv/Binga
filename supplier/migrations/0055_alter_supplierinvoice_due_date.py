# Generated by Django 3.2.12 on 2022-08-28 07:54

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('supplier', '0054_alter_supplierinvoice_due_date'),
    ]

    operations = [
        migrations.AlterField(
            model_name='supplierinvoice',
            name='due_date',
            field=models.DateTimeField(default=datetime.datetime(2022, 9, 27, 9, 54, 49, 130303), verbose_name='Due Date'),
        ),
    ]
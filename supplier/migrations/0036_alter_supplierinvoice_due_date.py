# Generated by Django 3.2.12 on 2022-08-17 10:10

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('supplier', '0035_alter_supplierinvoice_due_date'),
    ]

    operations = [
        migrations.AlterField(
            model_name='supplierinvoice',
            name='due_date',
            field=models.DateTimeField(default=datetime.datetime(2022, 9, 16, 12, 10, 31, 499136), verbose_name='Due Date'),
        ),
    ]
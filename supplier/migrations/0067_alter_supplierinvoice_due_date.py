# Generated by Django 3.2.12 on 2022-08-28 11:23

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('supplier', '0066_alter_supplierinvoice_due_date'),
    ]

    operations = [
        migrations.AlterField(
            model_name='supplierinvoice',
            name='due_date',
            field=models.DateTimeField(default=datetime.datetime(2022, 9, 27, 13, 23, 6, 67817), verbose_name='Due Date'),
        ),
    ]
# Generated by Django 3.2.12 on 2022-08-04 20:58

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('supplier', '0018_alter_supplierinvoice_due_date'),
    ]

    operations = [
        migrations.AlterField(
            model_name='supplierinvoice',
            name='due_date',
            field=models.DateTimeField(default=datetime.datetime(2022, 9, 3, 20, 58, 21, 62284), verbose_name='Due Date'),
        ),
    ]

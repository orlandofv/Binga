# Generated by Django 3.2.12 on 2022-07-14 12:13

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('supplier', '0008_alter_supplierinvoice_due_date'),
    ]

    operations = [
        migrations.AlterField(
            model_name='supplierinvoice',
            name='due_date',
            field=models.DateTimeField(default=datetime.datetime(2022, 8, 13, 12, 13, 18, 912011), verbose_name='Due Date'),
        ),
    ]
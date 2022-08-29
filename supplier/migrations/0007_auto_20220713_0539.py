# Generated by Django 3.2.12 on 2022-07-13 05:39

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('supplier', '0006_auto_20220713_0538'),
    ]

    operations = [
        migrations.AlterField(
            model_name='supplierinvoice',
            name='due_date',
            field=models.DateTimeField(default=datetime.datetime(2022, 8, 12, 5, 39, 28, 70969), verbose_name='Due Date'),
        ),
        migrations.AlterField(
            model_name='supplierinvoice',
            name='number',
            field=models.IntegerField(default=0, unique=True),
        ),
    ]
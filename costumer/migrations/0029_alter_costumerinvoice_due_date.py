# Generated by Django 3.2.12 on 2022-08-28 09:25

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('costumer', '0028_alter_costumerinvoice_due_date'),
    ]

    operations = [
        migrations.AlterField(
            model_name='costumerinvoice',
            name='due_date',
            field=models.DateTimeField(default=datetime.datetime(2022, 9, 27, 11, 25, 42, 917105), verbose_name='Due Date'),
        ),
    ]
# Generated by Django 3.2.12 on 2022-08-17 21:56

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('costumer', '0008_alter_costumerinvoice_due_date'),
    ]

    operations = [
        migrations.AlterField(
            model_name='costumerinvoice',
            name='due_date',
            field=models.DateTimeField(default=datetime.datetime(2022, 9, 16, 23, 56, 28, 778965), verbose_name='Due Date'),
        ),
    ]
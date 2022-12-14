# Generated by Django 3.2.12 on 2022-08-18 08:57

import datetime
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('isis', '0112_auto_20220818_0146'),
    ]

    operations = [
        migrations.AlterField(
            model_name='invoice',
            name='due_date',
            field=models.DateTimeField(default=datetime.datetime(2022, 9, 17, 10, 57, 50, 628248), verbose_name='Due Date'),
        ),
        migrations.AlterField(
            model_name='invoicing',
            name='due_date',
            field=models.DateTimeField(default=datetime.datetime(2022, 9, 17, 10, 57, 50, 623259), verbose_name='Due Date'),
        ),
        migrations.AlterField(
            model_name='product',
            name='category',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.PROTECT, to='isis.category', verbose_name='Product Category'),
        ),
    ]

# Generated by Django 3.2.12 on 2022-07-03 16:14

import datetime
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('isis', '0063_auto_20220703_1451'),
    ]

    operations = [
        migrations.AddField(
            model_name='document',
            name='short_name',
            field=models.CharField(default='', max_length=20, unique=True),
        ),
        migrations.AddField(
            model_name='invoicing',
            name='document',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.PROTECT, to='isis.document', verbose_name='Document'),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='invoice',
            name='due_date',
            field=models.DateTimeField(default=datetime.datetime(2022, 8, 2, 16, 14, 19, 268409), verbose_name='Due Date'),
        ),
        migrations.AlterField(
            model_name='invoicing',
            name='due_date',
            field=models.DateTimeField(default=datetime.datetime(2022, 8, 2, 16, 14, 19, 263441), verbose_name='Due Date'),
        ),
    ]

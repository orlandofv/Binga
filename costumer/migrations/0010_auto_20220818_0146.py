# Generated by Django 3.2.12 on 2022-08-17 23:46

import datetime
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('isis', '0112_auto_20220818_0146'),
        ('costumer', '0009_alter_costumerinvoice_due_date'),
    ]

    operations = [
        migrations.AlterField(
            model_name='costumerinvoice',
            name='due_date',
            field=models.DateTimeField(default=datetime.datetime(2022, 9, 17, 1, 46, 9, 970670), verbose_name='Due Date'),
        ),
        migrations.AlterField(
            model_name='costumerinvoice',
            name='payment_method',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.PROTECT, to='isis.paymentmethod', verbose_name='Payment method'),
        ),
        migrations.AlterField(
            model_name='costumerinvoice',
            name='payment_term',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.PROTECT, to='isis.paymentterm', verbose_name='Payment term'),
        ),
        migrations.AlterField(
            model_name='costumerreceipt',
            name='active_status',
            field=models.IntegerField(blank=True, default=1, verbose_name='Active status'),
        ),
        migrations.AlterField(
            model_name='costumerreceipt',
            name='finished_status',
            field=models.IntegerField(blank=True, default=0, verbose_name='Finished status'),
        ),
        migrations.AlterField(
            model_name='costumerreceipt',
            name='notes',
            field=models.TextField(blank=True, verbose_name='Notes'),
        ),
    ]

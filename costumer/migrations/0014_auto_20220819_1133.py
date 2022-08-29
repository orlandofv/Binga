# Generated by Django 3.2.12 on 2022-08-19 09:33

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('costumer', '0013_auto_20220819_1122'),
    ]

    operations = [
        migrations.AlterField(
            model_name='costumerinvoice',
            name='due_date',
            field=models.DateTimeField(default=datetime.datetime(2022, 9, 18, 11, 33, 19, 773113), verbose_name='Due Date'),
        ),
        migrations.AlterField(
            model_name='costumerinvoiceitem',
            name='discount',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=4),
        ),
        migrations.AlterField(
            model_name='costumerinvoiceitem',
            name='discount_total',
            field=models.DecimalField(decimal_places=6, default=0, max_digits=18),
        ),
        migrations.AlterField(
            model_name='costumerinvoiceitem',
            name='price',
            field=models.DecimalField(decimal_places=6, default=0, max_digits=18),
        ),
        migrations.AlterField(
            model_name='costumerinvoiceitem',
            name='quantity',
            field=models.DecimalField(decimal_places=6, default=0, max_digits=18),
        ),
        migrations.AlterField(
            model_name='costumerinvoiceitem',
            name='sub_total',
            field=models.DecimalField(decimal_places=6, default=0, max_digits=18),
        ),
        migrations.AlterField(
            model_name='costumerinvoiceitem',
            name='tax',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=4),
        ),
        migrations.AlterField(
            model_name='costumerinvoiceitem',
            name='tax_total',
            field=models.DecimalField(decimal_places=6, default=0, max_digits=18),
        ),
        migrations.AlterField(
            model_name='costumerinvoiceitem',
            name='total',
            field=models.DecimalField(decimal_places=6, default=0, max_digits=18),
        ),
    ]

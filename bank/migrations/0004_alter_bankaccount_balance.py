# Generated by Django 3.2.12 on 2022-07-14 14:05

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('bank', '0003_rename_total_balance_bankaccount_balance'),
    ]

    operations = [
        migrations.AlterField(
            model_name='bankaccount',
            name='balance',
            field=models.DecimalField(blank=True, decimal_places=6, default=0, editable=False, max_digits=18),
        ),
    ]

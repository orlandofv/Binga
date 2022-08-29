# Generated by Django 3.2.12 on 2022-07-14 12:13

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('asset_app', '0069_auto_20220622_0059'),
    ]

    operations = [
        migrations.AlterField(
            model_name='action',
            name='active_status',
            field=models.IntegerField(choices=[(1, 'Active'), (0, 'Inactive')], default=1, verbose_name='Status'),
        ),
        migrations.AlterField(
            model_name='allocation',
            name='active_status',
            field=models.IntegerField(choices=[(1, 'Active'), (0, 'Inactive')], default=1, verbose_name='Status'),
        ),
        migrations.AlterField(
            model_name='component',
            name='active_status',
            field=models.IntegerField(choices=[(1, 'Active'), (0, 'Inactive')], default=1, verbose_name='Status'),
        ),
        migrations.AlterField(
            model_name='costumer',
            name='active_status',
            field=models.IntegerField(choices=[(1, 'Active'), (0, 'Inactive')], default=1, verbose_name='Status'),
        ),
        migrations.AlterField(
            model_name='item',
            name='active_status',
            field=models.IntegerField(choices=[(1, 'Active'), (0, 'Inactive')], default=1, verbose_name='Status'),
        ),
        migrations.AlterField(
            model_name='maintenance',
            name='active_status',
            field=models.IntegerField(choices=[(1, 'Active'), (0, 'Inactive')], default=1, verbose_name='Status'),
        ),
        migrations.AlterField(
            model_name='maintenanceitem',
            name='active_status',
            field=models.IntegerField(choices=[(1, 'Active'), (0, 'Inactive')], default=1, verbose_name='Status'),
        ),
        migrations.AlterField(
            model_name='settings',
            name='active_status',
            field=models.IntegerField(choices=[(1, 'Active'), (0, 'Inactive')], default=1, verbose_name='Status'),
        ),
        migrations.AlterField(
            model_name='vendor',
            name='active_status',
            field=models.IntegerField(choices=[(1, 'Active'), (0, 'Inactive')], default=1, verbose_name='Status'),
        ),
        migrations.AlterField(
            model_name='workorder',
            name='active_status',
            field=models.IntegerField(choices=[(1, 'Active'), (0, 'Inactive')], default=1, verbose_name='Active Status'),
        ),
    ]

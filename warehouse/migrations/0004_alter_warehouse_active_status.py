# Generated by Django 3.2.12 on 2022-07-14 12:13

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('warehouse', '0003_alter_userwarehouse_unique_together'),
    ]

    operations = [
        migrations.AlterField(
            model_name='warehouse',
            name='active_status',
            field=models.IntegerField(choices=[(1, 'Active'), (0, 'Inactive')], default=1),
        ),
    ]

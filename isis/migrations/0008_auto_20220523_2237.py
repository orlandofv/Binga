# Generated by Django 3.2.12 on 2022-05-23 22:37

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('isis', '0007_rename_parent_wharehouse_warehouse_parent_warehouse'),
    ]

    operations = [
        migrations.AlterField(
            model_name='tax',
            name='name',
            field=models.CharField(max_length=25, unique=True),
        ),
        migrations.AlterField(
            model_name='warehouse',
            name='name',
            field=models.CharField(max_length=25, unique=True),
        ),
    ]
# Generated by Django 3.2.12 on 2022-05-21 11:33

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('asset_app', '0044_item_cost'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='action',
            name='cost',
        ),
    ]

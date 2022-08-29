# Generated by Django 3.2.12 on 2022-06-24 00:49

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('warehouse', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='UserWarehouse',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to=settings.AUTH_USER_MODEL)),
                ('warehouse', models.ForeignKey(null=True, on_delete=django.db.models.deletion.PROTECT, to='warehouse.warehouse', verbose_name='Default Warehouse')),
            ],
        ),
    ]
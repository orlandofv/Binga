# Generated by Django 3.2.12 on 2022-06-01 08:45

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Warehouse',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=25, unique=True)),
                ('slug', models.SlugField(editable=False, unique=True)),
                ('parent', models.IntegerField(default=0)),
                ('description', models.TextField(blank=True)),
                ('address', models.CharField(blank=True, max_length=255)),
                ('contacts', models.CharField(blank=True, max_length=255)),
                ('active_status', models.IntegerField(choices=[(1, 'Active'), (0, 'Deactivated')], default=1)),
                ('open_status', models.CharField(choices=[('OPEN', 'Open'), ('CLOSE', 'Close')], default='OPEN', max_length=25)),
                ('notes', models.TextField(blank=True)),
                ('date_created', models.DateTimeField(default=django.utils.timezone.now, editable=False)),
                ('date_modified', models.DateTimeField(default=django.utils.timezone.now, editable=False)),
                ('created_by', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='+', to=settings.AUTH_USER_MODEL)),
                ('modified_by', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='+', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ('name',),
            },
        ),
    ]
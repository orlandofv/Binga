# Generated by Django 3.2.12 on 2022-04-19 20:36

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('asset_app', '0027_auto_20220419_2015'),
    ]

    operations = [
        migrations.CreateModel(
            name='WorkOrder',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('order', models.IntegerField(unique=True, verbose_name='Order Number')),
                ('start', models.DateTimeField(default=django.utils.timezone.now, verbose_name='Start date')),
                ('end', models.DateTimeField(default=django.utils.timezone.now, verbose_name='End date')),
                ('warn_after', models.DateTimeField(default=django.utils.timezone.now, verbose_name='Warn After')),
                ('status', models.CharField(choices=[('Pending', 'Pending'), ('InProgress', 'InProgress'), ('Finished', 'Finished'), ('Abandoned', 'Abandoned')], default='Pending', max_length=15)),
                ('notes', models.TextField(blank=True)),
                ('date_created', models.DateTimeField(default=django.utils.timezone.now, editable=False)),
                ('date_modified', models.DateTimeField(default=django.utils.timezone.now, editable=False)),
                ('allocation', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='asset_app.allocation', verbose_name='Allocation')),
                ('created_by', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='+', to=settings.AUTH_USER_MODEL)),
                ('modified_by', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='+', to=settings.AUTH_USER_MODEL)),
                ('responsible', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to=settings.AUTH_USER_MODEL, verbose_name='Person in Charge')),
            ],
            options={
                'verbose_name': 'Work Order',
                'verbose_name_plural': 'Work Orders',
                'ordering': ('-start',),
            },
        ),
        migrations.DeleteModel(
            name='MaintenanceOrder',
        ),
    ]
# Generated by Django 3.2.12 on 2022-04-16 15:56

from django.conf import settings
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('asset_app', '0019_alter_companysettings_address'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='CompanySettings',
            new_name='Settings',
        ),
    ]
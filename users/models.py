# -*- coding: utf-8 -*-
import datetime
from email.mime import image
from operator import mod
import re
from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models
from django.utils.translation import ugettext as _
from django.core import exceptions
from django.db.models.signals import post_save
from django.dispatch import receiver
from phonenumber_field.modelfields import PhoneNumberField
from django.conf import settings
from django.utils import timezone
from django.template.defaultfilters import slugify # new
from django.urls import reverse


GENDER_CHOICES = (
    (1, _("Male")),
    (2, _("Female"))
)

class UserManager(BaseUserManager):
    """Define a model manager for User model with no username field."""

    use_in_migrations = True

    def _create_user(self, email, password, **extra_fields):
        """Create and save a User with the given email and password."""
        if not email:
            raise ValueError('The given email must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email, password=None, **extra_fields):
        """Create and save a regular User with the given email and password."""
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', False)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('User must have is_staff=True.')

        return self._create_user(email, password, **extra_fields)

    def create_superuser(self, email, password, **extra_fields):
        """Create and save a SuperUser with the given email and password."""
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self._create_user(email, password, **extra_fields)


class User(AbstractUser):
    """We change the default user auth by email auth"""
    EMPLOYEE_CHOICES = ((1, 'Yes'), (2, 'No'))
    TITLE_CHOICES = (('mr', 'Mr.'), ('miss', 'Miss'), 
    ('dr', 'dr.'), ('Dr', 'Dr.'),)

    last_active = datetime.datetime.now() + datetime.timedelta(days=365)

    username = models.CharField(_('Username'), max_length=20, blank=True, unique=True)
    email = models.EmailField(_('Email'), unique=True, help_text=False)
    image = models.ImageField(_('Image'), default="{}default.jpg".format(settings.MEDIA_URL), 
    upload_to = 'images/% Y/% m/% d/')
    title = models.CharField(_('Title'), max_length=10, blank=True, choices=TITLE_CHOICES, default='mr')
    gender = models.IntegerField(_('Gender'), blank=True, choices=GENDER_CHOICES, default=1)
    employee = models.IntegerField(_('Employee'), blank=True, choices=EMPLOYEE_CHOICES, 
    default=1)
    first_active_date = models.DateTimeField(_('First Active Date'), blank=True, 
    default=timezone.now)
    last_active_date = models.DateTimeField(_('Last Active Date'), blank=True, 
    default=last_active)
    country = models.CharField(_('Country'), max_length=100, blank=True)
    province = models.CharField(_('Province/State'), max_length=100, blank=True)
    city = models.CharField(_('City'), max_length=100, blank=True)
    zip = models.CharField(_('Zip Code'), max_length=100, blank=True)
    address = models.CharField(_('Address'), blank=True, max_length=255)
    phone = models.CharField(_('Phone'), blank=True, max_length=255)
    fax = models.CharField(_('Fax'), blank=True, max_length=255)
    mobile = models.CharField(_('Mobile'), blank=True, max_length=255)
    vat = models.CharField(_("VAT Number"), max_length=15, blank=True)
    website = models.CharField(_('Website'), max_length = 254, blank=True)
    date_created = models.DateTimeField(editable=False, 
    default=timezone.now)
    date_modified = models.DateTimeField(editable=False, 
    default=timezone.now)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []
    objects = UserManager()

    def get_full_name(self):
        if self.first_name is not None or self.first_name != "":
            return '{} {}'.format(self.first_name, self.last_name)
        else:
            return self.username

    def __str__(self):
        return self.username

    def get_absolute_url(self):
        return reverse('user_details', kwargs={'pk': self.id})

    class Meta:
        ordering = ('-username',)

    @property
    def is_anonymous(self):
        if self.email == None:
            return True
        else:
            return False



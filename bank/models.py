# -*- coding: utf-8 -*-
from random import choices
from django.db import models
from django.urls import reverse
from django.template.defaultfilters import slugify # new
from django.utils.translation import ugettext_lazy as _
from django.utils import timezone

from users.models import User
from asset_app.models import Costumer


ACTIVE = 1
DEACTIVATED  = 0

STATUSES = ((ACTIVE, _('Active')), (DEACTIVATED , _('Inactive')))


class Bank(models.Model):
    name = models.CharField(_('Bank Name'), max_length=100, unique=True)
    slug = models.SlugField(unique=True, null=False, editable=False)
    address = models.CharField(_('Address'), max_length=255, blank=True)
    email = models.EmailField(_('Email'), max_length=255, blank=True)
    website = models.URLField(_('Website'), max_length=255, blank=True)
    telephone = models.CharField(_('Telephone'), max_length=255, blank=True)
    fax = models.CharField(_('Fax'), max_length=255, blank=True)
    cell = models.CharField(_('Cell'), max_length=255, blank=True)
    active_status = models.IntegerField(_('Status'), choices=STATUSES, default=ACTIVE)
    notes = models.TextField(_('Notes'), blank=True)
    date_created = models.DateTimeField(editable=False, default=timezone.now)
    date_modified = models.DateTimeField(editable=False, default=timezone.now)
    created_by = models.ForeignKey(User, on_delete=models.PROTECT, related_name="+")
    modified_by = models.ForeignKey(User, on_delete=models.PROTECT, related_name="+")

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('bank_details', kwargs={'slug': self.slug})

    def save(self, *args, **kwargs): # new
        if not self.slug:
            self.slug = slugify(self.name)
        return super().save(*args, **kwargs)

    class Meta:
        ordering = ("name",)


class BankAccount(models.Model):
    CHECKING = 1
    SAVINGS = 2
    MONEY_MARKET = 3
    CERTIFICATE_OF_DEPOSIT = 4
    
    ACC_TYPE_CHOICES = ((CHECKING, _("Checking")), (SAVINGS, _('Savings')), 
    (MONEY_MARKET, _("Money Market")), (CERTIFICATE_OF_DEPOSIT, _("Certificate of Deposit")))

    INACTIVE = 0
    ACTIVE = 1
    SUSPENDED = 2

    ACC_STATUSES = ((ACTIVE, _('Active')), (INACTIVE, _('Inactive')), 
    (SUSPENDED, _('Suspended')))

    acc_no = models.CharField(_('Account'), max_length=50, unique=True, blank=False)
    slug = models.SlugField(unique=True, null=False, editable=False)
    bank = models.ForeignKey(Bank, verbose_name=('Bank'), on_delete=models.PROTECT)
    acc_nib = models.CharField(_('NIB'),max_length=50, blank=True)
    acc_iban = models.CharField(_('IBAN'), max_length=50, blank=True)
    acc_swift = models.CharField(_('SWIFT'), max_length=50, blank=True)
    acc_type = models.IntegerField(_('Account Type'), default=1, choices=ACC_TYPE_CHOICES)
    acc_status = models.IntegerField(_('Account Status'), default=1, choices=ACC_STATUSES)
    balance = models.DecimalField(max_digits=18, decimal_places=6, default=0, editable=False, blank=True)
    notes = models.TextField(_('Notes'), blank=True)
    date_created = models.DateTimeField(editable=False, default=timezone.now)
    date_modified = models.DateTimeField(editable=False, default=timezone.now)
    created_by = models.ForeignKey(User, on_delete=models.PROTECT, related_name="+")
    modified_by = models.ForeignKey(User, on_delete=models.PROTECT, related_name="+")

    def __str__(self):
        return '{}, {}'.format(self.bank, self.acc_no)

    def get_absolute_url(self):
        return reverse('account_details', kwargs={'slug': self.slug})

    def save(self, *args, **kwargs): # new
        if not self.slug:
            self.slug = slugify('{}'.format(self.acc_no))
        return super().save(*args, **kwargs)

    class Meta:
        ordering = ("acc_no",)
        verbose_name_plural = _("Bank Accounts")


    def get_acc_type(self):
        if self.acc_type == self.CHECKING:
            return _('Checking')
        elif self.acc_type == self.SAVINGS:
            return _('Savings')
        elif self.acc_type == self.MONEY_MARKET:
            return _('Money Market')
        elif self.acc_type == self.CERTIFICATE_OF_DEPOSIT:
            return _('Certificate Of Deposit')
    
    def get_acc_status(self):
        if self.acc_status == self.INACTIVE:
            return _('Inactive')
        elif self.acc_type == self.ACTIVE:
            return _('Active')
        elif self.acc_type == self.SUSPENDED:
            return _('Suspended')


class BankTransaction(models.Model):
    account = models.ForeignKey(BankAccount, on_delete=models.PROTECT)
    debit = models.DecimalField(max_digits=18, decimal_places=6, default=0)
    credit = models.DecimalField(max_digits=18, decimal_places=6, default=0)
    notes = models.TextField(_('Notes'), blank=True)
    date_created = models.DateTimeField(editable=False, default=timezone.now)
    date_modified = models.DateTimeField(editable=False, default=timezone.now)
    created_by = models.ForeignKey(User, on_delete=models.PROTECT, related_name="+")
    modified_by = models.ForeignKey(User, on_delete=models.PROTECT, related_name="+")

    def __str__(self):
        return "{}, {} - {}".format(self.account, self.costumer, self.amount)
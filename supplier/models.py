# -*- coding: utf-8 -*-
from decimal import Decimal
import datetime


from django.db import models
from django.utils import timezone
from users.models import User
from django.urls import reverse
from django.template.defaultfilters import slugify # new
from django.utils.translation import ugettext_lazy as _

from asset_app.models import Costumer
from isis.models import PaymentMethod, PaymentTerm, Product, Warehouse, Tax
from bank.models import BankAccount


class SupplierInvoice(models.Model):
    DELIVERED = 1
    NOT_DELIVERED = 0

    DELIVERED_STATUS = ((DELIVERED, _('Delivered')), (NOT_DELIVERED, _('Not delivered')))

    invoice = models.CharField('Invoice Number', help_text='Supplier Invoice Number(Ex: Invoice: 12345)', 
    max_length=100)
    number = models.IntegerField(default=0, unique=True)
    payment_method = models.ForeignKey(PaymentMethod, on_delete=models.PROTECT, default=1, verbose_name=_('Payment method'))
    payment_term = models.ForeignKey(PaymentTerm, on_delete=models.PROTECT, default=1, verbose_name=_('Payment term'))
    supplier = models.ForeignKey(verbose_name=_('Supplier'), to=Costumer, on_delete=models.PROTECT, default=1)
    date = models.DateTimeField(_('Date'), default=timezone.now)
    due_date = models.DateTimeField(_('Due Date'), 
    default=datetime.datetime.now() + datetime.timedelta(days=30))
    warehouse = models.ForeignKey(Warehouse, on_delete=models.PROTECT, default=1)
    credit = models.DecimalField(max_digits=18, decimal_places=6, default=0, blank=True)
    debit = models.DecimalField(max_digits=18, decimal_places=6, default=0, blank=True)
    total = models.DecimalField(max_digits=18, decimal_places=6, default=0, blank=True)
    total_tax = models.DecimalField(max_digits=18, decimal_places=6, default=0, blank=True)
    subtotal = models.DecimalField(max_digits=18, decimal_places=6, default=0, blank=True)
    total_discount = models.DecimalField(max_digits=18, decimal_places=6, default=0, blank=True)
    paid_status = models.IntegerField(default=0)
    delivered_status = models.IntegerField(default=0)
    finished_status = models.IntegerField(default=0)
    active_status = models.IntegerField(default=1)
    notes = models.TextField(_('Private Notes'), blank=True)
    public_notes = models.TextField(_('Public Notes'), blank=True)
    date_created = models.DateTimeField(editable=False, default=timezone.now)
    date_modified = models.DateTimeField(editable=False, default=timezone.now)
    created_by = models.ForeignKey(User, on_delete=models.PROTECT, related_name="+")
    modified_by = models.ForeignKey(User, on_delete=models.PROTECT, related_name="+")
    bank_account =  models.ForeignKey(BankAccount, verbose_name=_('Bank Account'),  on_delete=models.PROTECT, 
    null=True, blank=True)
    
    
    def is_overdue(self):
        if datetime.datetime.now() > self.due_date:
            return True
        else:
            return False
    
    @property
    def overdue_status(self):
        if self.is_overdue():
            overdue = _('Overdue')
        else:
            overdue = _('On date')

        return overdue

    def is_paid(self):
        if self.credit == self.total:
            return True
        return False

    @property
    def payment_status(self):
        if self.debit == self.total:
            paid = _('Not paid')
        elif self.debit == 0:
            paid = ('Paid Totally')
        else:
            paid = ('Paid Partially')

        return paid

    def is_delivered(self):
        if self.delivered_status == 1:
            return True
        else:
            return False

    @property
    def delivery_status(self):
        if self.is_delivered():
            delivered = _('Delivered')
        else:
            delivered = _('Not Delivered')
        
        return delivered
    
    def is_active(self):
        if self.active_status == 1:
            active = _('Active')
        else:
            active = _('Canceled')

        return active
    
    @property
    def is_finished(self):
        if self.finished_status == 1:
            return True
        else:
            return False

    def __str__(self):
        return str(self.number)

    class Meta:
        ordering = ('number',)
        unique_together = ('invoice', 'supplier')


class SupplierInvoiceItem(models.Model):
    invoice = models.ForeignKey(SupplierInvoice, on_delete=models.PROTECT)
    product = models.ForeignKey(Product, on_delete=models.PROTECT)
    tax = models.DecimalField(max_digits=4, decimal_places=2, default=0)
    discount = models.DecimalField(max_digits=4, decimal_places=2, default=0)
    price = models.DecimalField(max_digits=18, decimal_places=6, default=0)
    quantity = models.DecimalField(max_digits=18, decimal_places=6, default=0)
    tax_total = models.DecimalField(max_digits=18, decimal_places=6, default=0)
    discount_total = models.DecimalField(max_digits=18, decimal_places=6, default=0)
    sub_total = models.DecimalField(max_digits=18, decimal_places=6, default=0)
    total = models.DecimalField(max_digits=18, decimal_places=6, default=0)
        
    def save(self, *args, **kwargs): # new
        print("Nao sei que corre antes {}".format(self.invoice.number))
        # Discount is saved on db as whole number so we must divide by 100
        total = round(self.quantity * self.price, 6)
        print('Total: ', total)

        discount = round(self.discount * Decimal(0.01) * total, 6)
        print('Discount ', discount)

        sub_total = round(total - discount, 6)
        print('Subtotal ', sub_total)

        tax = round(sub_total * self.tax * Decimal(0.01), 6)
        print('Tax ', tax)
        
        grand_total = sub_total + tax
        print('Grand Total ', grand_total)

        self.tax_total = tax
        self.discount_total = discount
        self.sub_total = sub_total
        self.total = grand_total

        return super().save(*args, **kwargs)


class SupplierReceipt(models.Model):
    number = models.IntegerField(unique=True, default=0)
    supplier = models.ForeignKey(Costumer, on_delete=models.PROTECT, default=1)
    notes = models.TextField(_('Notes'), blank=True)
    date_created = models.DateTimeField(editable=False, default=timezone.now)
    date_modified = models.DateTimeField(editable=False, default=timezone.now)
    created_by = models.ForeignKey(User, on_delete=models.PROTECT, related_name="+")
    modified_by = models.ForeignKey(User, on_delete=models.PROTECT, related_name="+")
    active_status = models.IntegerField(_('Active status'), default=1, blank=True)
    finished_status = models.IntegerField(_('Finished status'), default=0, blank=True)
    bank_account =  models.ForeignKey(BankAccount, verbose_name=_('Bank Account'),  on_delete=models.PROTECT, 
    null=True, blank=True)
    
    
    @property
    def is_active(self):
        if self.active_status == 1:
            return True
        else:
            return False
    
    @property
    def is_inactive(self):
        return not self.is_active

    @property
    def is_finished(self):
        if self.finished_status == 1:
            return True
        else:
            return False

    def __str__(self):
        return str(self.number)


class SupplierReceiptInvoice(models.Model):
    invoice = models.ForeignKey(SupplierInvoice, on_delete=models.PROTECT)
    receipt = models.ForeignKey(SupplierReceipt, on_delete=models.PROTECT)
    debit = models.DecimalField(max_digits=18, decimal_places=6, default=0)
    remaining = models.DecimalField(max_digits=18, decimal_places=6, default=0)
    paid = models.DecimalField(max_digits=18, decimal_places=6, default=0)
    description = models.CharField(_('Description'), max_length=255, blank=True)

    def __str__(self):
        return "{}".format(self.invoice, self.receipt)
    
    class Meta:
        verbose_name = _('Supplier Receipt Invoice')
        verbose_name_plural = _('Supplier Receipt Invoices')
        unique_together = ['receipt', 'invoice']




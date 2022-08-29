# -*- coding: utf-8 -*-
from decimal import Decimal
import datetime

from django.db import models
from django.utils import timezone
from users.models import User
from django.urls import reverse
from django.template.defaultfilters import slugify # new
from django.utils.translation import ugettext_lazy as _
from django.db.models.signals import post_save, post_init
from django.dispatch import receiver
from django.utils.functional import lazy
from django.conf import settings

from asset_app.models import Costumer
from warehouse.models import Warehouse
from bank.models import BankAccount


ACTIVE = 1
DEACTIVATED  = 0

STATUSES = ((ACTIVE, _('Active')), (DEACTIVATED , _('Inactive')))

DEFAULT = 1
NOT_DEFAULT = 0

DEFAULT_CHOICES = ((DEFAULT, _('Yes')), (NOT_DEFAULT, _('No')))

class Tax(models.Model):
    
    name = models.CharField(_('Name'), max_length=25, unique=True)
    slug = models.SlugField(unique=True, null=False, editable=False)
    rate = models.DecimalField(_('Rate'), max_digits=4, decimal_places=2, default=0, unique=True)
    active_status = models.IntegerField(_('Status'), choices=STATUSES, default=ACTIVE)
    notes = models.TextField(_('Notes'), blank=True)
    date_created = models.DateTimeField(editable=False, default=timezone.now)
    date_modified = models.DateTimeField(editable=False, default=timezone.now)
    created_by = models.ForeignKey(User, on_delete=models.PROTECT, related_name="+")
    modified_by = models.ForeignKey(User, on_delete=models.PROTECT, related_name="+")

    def __str__(self):
        return '{}'.format(self.name)

    def get_absolute_url(self):
        return reverse('tax_details', kwargs={'slug': self.slug})

    def save(self, *args, **kwargs): # new
        if not self.slug:
            self.slug = slugify(self.name) 
        return super().save(*args, **kwargs)

    class Meta:
        ordering = ("name",)


class Gallery(models.Model):
    image = models.ImageField(_('Image'), default="{}default.jpg".format(settings.MEDIA_URL), upload_to = 'media')
    date_created = models.DateTimeField(editable=False, default=timezone.now)
    date_modified = models.DateTimeField(editable=False, default=timezone.now)
    created_by = models.ForeignKey(User, on_delete=models.PROTECT, related_name="+")
    modified_by = models.ForeignKey(User, on_delete=models.PROTECT, related_name="+")

    class Meta:
        verbose_name_plural = 'Gallery'
        ordering = ("-date_created",)


class Category(models.Model):
    name = models.CharField(_('Name'), max_length=255, unique=True)
    parent = models.IntegerField(_('Parent'), default=0, blank=True)
    slug = models.SlugField(unique=True, null=False, editable=False)
    image = models.ImageField(_('Image'), default="{}default.jpg".format(settings.MEDIA_URL), 
    upload_to = 'media', blank=True)
    active_status = models.IntegerField(_('Active status'), choices=STATUSES, default=ACTIVE)
    notes = models.TextField(_('Notes'), blank=True)
    date_created = models.DateTimeField(editable=False, default=timezone.now)
    date_modified = models.DateTimeField(editable=False, default=timezone.now)
    created_by = models.ForeignKey(User, on_delete=models.PROTECT, related_name="+")
    modified_by = models.ForeignKey(User, on_delete=models.PROTECT, related_name="+")

    def get_parent(self):
        if self.parent in ("", 0, None):
            return '--'
        else:
            return Category.objects.filter(id=self.parent).first()

    def __str__(self):
        return '{}'.format(self.name)

    def get_absolute_url(self):
        return reverse('category_details', kwargs={'slug': self.slug})

    def save(self, *args, **kwargs): # new
        if not self.slug:
            self.slug = slugify(self.name) 
        return super().save(*args, **kwargs)

    class Meta:
        ordering = ("name",)
        verbose_name_plural = _('Categories')


class Product(models.Model):

    SERVICE = 'SERVICE'
    PRODUCT = 'PRODUCT'

    PRODUCT_CHOICES = ((SERVICE, _('Service')), (PRODUCT, _('Product')))
    
    FOR_SALE = FOR_PURCHASE = 1
    NOT_FOR_SALE = NOT_FOR_PURCHASE = 0

    TON ='ton'
    KG ='kg'
    G ='g'
    MG ='mg'
    PD ='pound'
    OUNCE ='ounce'

    M = 'm'
    DM = 'dm'
    CM = 'cm'
    MM = 'mm'
    FOOT ='ft'
    INCH ='in'
    
    M2 = 'm2'
    DM2 = 'dm2'
    CM2 = 'cm2'
    MM2 = 'mm2'
    FOOT2 ='ft2'
    INCH2 ='in2'
    
    M3 = 'm3'
    DM3 = 'dm3'
    CM3 = 'cm3'
    MM3 = 'mm3'
    FOOT3 ='ft3'
    INCH3 ='in3'
    LITRE ='litre'
    GALLON = 'gallon'


    WEIGHT_MEASUREMENT_CHOICES = ((KG, _('Kg')), (G, _('G')), (MG, _('MG')), (OUNCE, _('ounce')), 
    (PD, _('pound')), (TON, _('ton')))

    LENGTH_CHOICES = ((M, _('m')), (DM, _('dm')), (CM, _('cm')), (MM, _('mm')), (FOOT, _('ft')), 
    (INCH, _('in')))
    
    AREA_CHOICES = ((M2, _('m²')), (DM2, _('dm²')), (CM2, _('cm²')), (MM2, _('mm²')), (FOOT2, _('ft²')), 
    (INCH2, _('in²')))
    
    VOLUME_CHOICES = ((M3, _('m³')), (DM3, _('dm³')), (CM3, _('cm³')), (MM3, _('mm³')), (FOOT3, _('ft³')), 
    (INCH3, _('in³')), (LITRE, _('litre')), (GALLON, _('gallon')))

    RAW_PRODUCT = 'Raw Product'
    MANUFACTURED_PRODUCT = 'Manufactured Product'
    
    SELL_STATUSES = ((FOR_SALE, _('For Sale')), (NOT_FOR_SALE, _('Not for Sale')))
    PURCHASE_STATUSES = ((FOR_PURCHASE, _('For Purchase')), (NOT_FOR_PURCHASE, _('Not for Purchase')))

    PRODUCT_NATURE = ((RAW_PRODUCT, _('Raw Product')), (MANUFACTURED_PRODUCT, _('Manufactured Product')))
    
    code = models.CharField(_('Product Code'), max_length=50, unique=True)
    category = models.ForeignKey(Category, verbose_name=_('Product Category'), 
    on_delete=models.PROTECT, default=1)
    name = models.CharField(_('Name of Product'), max_length=255, unique=True, blank=False, null=False)
    type = models.CharField(_('Type'),choices=PRODUCT_CHOICES, max_length=10,  default=PRODUCT)
    slug = models.SlugField(unique=True, null=False, editable=False)
    tax = models.ForeignKey(Tax, verbose_name=_('Tax'), on_delete=models.PROTECT)
    warehouse = models.ForeignKey(Warehouse, verbose_name=_('Default Warehouse'), 
    on_delete=models.PROTECT, null=True, blank=True)
    description = models.TextField(_("Detailed Description"), blank=True)
    barcode = models.CharField(_("Barcode"), max_length=255, blank=True)
    sell_price = models.DecimalField(_('Sell price'), max_digits=18, decimal_places=6, default=0)
    min_sell_price = models.DecimalField(_('Min. Sell price'), max_digits=18, decimal_places=6, default=0)
    sell_price2 = models.DecimalField(_('Sell price 2'), max_digits=18, decimal_places=6, default=0)
    sell_price3 = models.DecimalField(_('Sell price 3'), max_digits=18, decimal_places=6, default=0)
    sell_price4 = models.DecimalField(_('Sell price 4'), max_digits=18, decimal_places=6, default=0)
    sell_price5 = models.DecimalField(_('Sell price 5'), max_digits=18, decimal_places=6, default=0)
    purchase_price = models.DecimalField(_('Purchase price'), max_digits=18, decimal_places=6, default=0)
    max_purchase_price = models.DecimalField(_('Max. purchase price'), max_digits=18, decimal_places=6, default=0)
    physical_stock = models.DecimalField(_('Physical stock'), max_digits=18, decimal_places=6, default=0)
    min_stock = models.DecimalField(_('Min. Stock'), max_digits=18, decimal_places=6, default=0)
    stock_limit = models.DecimalField(_('Stock limit'), max_digits=18, decimal_places=6, default=0)
    desired_stock = models.DecimalField(_('Desired stock'), max_digits=18, decimal_places=6, default=0)
    image = models.ImageField(_('Primary Image'), default="{}default.jpg".format(settings.MEDIA_URL), upload_to = 'media', blank=True)
    product_nature = models.CharField(_('Product nature'), max_length=50, choices=PRODUCT_NATURE, default=RAW_PRODUCT, blank=True)
    product_url = models.URLField(_('Product url'), max_length=255, blank=True)
    weight = models.DecimalField(_('Weight'), max_digits=9, decimal_places=6, default=0)
    length = models.DecimalField(_('Length'), max_digits=9, decimal_places=6, default=0)
    width = models.DecimalField(_('width'), max_digits=9, decimal_places=6, default=0)
    height = models.DecimalField(_('Height'), max_digits=9, decimal_places=6, default=0)
    length_units = models.CharField(_('Length units'), max_length=10, choices=LENGTH_CHOICES, default=M, blank=True)
    area = models.DecimalField(_('Area'), max_digits=9, decimal_places=6, default=0)
    area_units = models.CharField(_('Area units'), max_length=10, choices=AREA_CHOICES, default=M2, blank=True)
    volume = models.DecimalField(_('Volume'), max_digits=9, decimal_places=6, default=0)
    volume_units = models.CharField(_('Volume units'), max_length=10, choices=VOLUME_CHOICES, default=0, blank=True)
    weight_units = models.CharField(_('Weight units'), max_length=50, choices=WEIGHT_MEASUREMENT_CHOICES, default=KG, blank=True)
    active_status = models.IntegerField(_('Active status'), choices=STATUSES, default=ACTIVE)
    sell_status = models.IntegerField(_('Sell status'), choices=SELL_STATUSES, default=FOR_SALE)
    purchase_status = models.IntegerField(_('Purchase status'), choices=PURCHASE_STATUSES, default=FOR_PURCHASE)
    notes = models.TextField(_('Notes'), blank=True)
    date_created = models.DateTimeField(editable=False, auto_now_add=True)
    date_modified = models.DateTimeField(editable=False, auto_now_add=True)
    created_by = models.ForeignKey(User, on_delete=models.PROTECT, related_name="+")
    modified_by = models.ForeignKey(User, on_delete=models.PROTECT, related_name="+")

    @property
    def is_product(self):
        if self.type == 'SERVICE':
            return False
        else:
            return True

    def is_active(self):
        if self.active_status == 1:
            return _('Active')
        else:
            return _('Inactive')

    @property
    def is_inactive(self):
        if self.active_status == 0:
            return True
        else:
            return False

    @property
    def is_not_for_sale(self):
        if self.sell_status == 0:
            return True
        else:
            return False

    @property
    def is_not_for_purchase(self):
        if self.purchase_status == 0:
            return True
        else:
            return False

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('product_details', kwargs={'slug': self.slug})

    def save(self, *args, **kwargs): # new
        if not self.slug:
            self.slug = slugify(self.name)
        return super().save(*args, **kwargs)

    class Meta:
        ordering = ("name",)


class PaymentTerm(models.Model):
    name = models.CharField(_('Name'), max_length=100, unique=True)
    slug = models.SlugField(unique=True, null=False, editable=False)
    notes = models.CharField(_('Notes'), blank=True, max_length=255)
    date_created = models.DateTimeField(editable=False, default=timezone.now)
    date_modified = models.DateTimeField(editable=False, default=timezone.now)
    created_by = models.ForeignKey(User, on_delete=models.PROTECT, related_name="+")
    modified_by = models.ForeignKey(User, on_delete=models.PROTECT, related_name="+")
    active_status = models.IntegerField(_('Active status'), choices=STATUSES, default=ACTIVE)
    default = models.IntegerField(_('Default'), choices=DEFAULT_CHOICES, default=NOT_DEFAULT, blank=True)

    def is_default(self):
        if self.default == 1:
            return True
        else:
            return False

    @property
    def get_default(self):
        if self.is_default():
            return _('Yes')
        else:
            return _('No')


    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('payment_term_details', kwargs={'slug': self.slug})

    def save(self, *args, **kwargs): # new
        if not self.slug:
            self.slug = slugify(self.name)
        return super().save(*args, **kwargs)

    class Meta:
        ordering = ("name",)


class PaymentMethod(models.Model):
    name = models.CharField(_('Name'), max_length=100, unique=True)
    slug = models.SlugField(unique=True, null=False, editable=False)
    notes = models.TextField(_('Notes'), blank=True)
    date_created = models.DateTimeField(editable=False, default=timezone.now)
    date_modified = models.DateTimeField(editable=False, default=timezone.now)
    created_by = models.ForeignKey(User, on_delete=models.PROTECT, related_name="+")
    modified_by = models.ForeignKey(User, on_delete=models.PROTECT, related_name="+")
    active_status = models.IntegerField(_('Active status'), choices=STATUSES, default=ACTIVE)
    default = models.IntegerField(_('Default'), choices=DEFAULT_CHOICES, default=NOT_DEFAULT, blank=True)

    def is_default(self):
        if self.default == 1:
            return True
        else:
            return False

    @property
    def get_default(self):
        if self.is_default():
            return _('Yes')
        else:
            return _('No')

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('payment_method_details', kwargs={'slug': self.slug})

    def save(self, *args, **kwargs): # new
        if not self.slug:
            self.slug = slugify(self.name)
        return super().save(*args, **kwargs)

    class Meta:
        ordering = ("name",)



class Document(models.Model):
    YES = 1
    NO = 0

    TRACK_STATUS = ((YES, _('Yes')), (NO, _('No')))

    name =  models.CharField(_('Name'),max_length=20, unique=True)
    short_name =  models.CharField(_('Short Name'), max_length=10, unique=True, default="")
    slug = models.SlugField(unique=True, null=False, editable=False)
    # Checks if the document modifies stock or not
    modify_stock = models.IntegerField(_("Modify Stock?"), choices=TRACK_STATUS, default=NO)
    active_status = models.IntegerField(_('Active status'), choices=STATUSES, default=ACTIVE)
    notes = models.TextField(_('Notes'), blank=True)
    date_created = models.DateTimeField(editable=False, default=timezone.now)
    date_modified = models.DateTimeField(editable=False, default=timezone.now)
    created_by = models.ForeignKey(User, on_delete=models.PROTECT, related_name="+")
    modified_by = models.ForeignKey(User, on_delete=models.PROTECT, related_name="+")
    track_payment = models.IntegerField(_('Track Payment?'), default=NO, choices=TRACK_STATUS)
    track_due_date = models.IntegerField(_('Track Due Date?'), default=NO, choices=TRACK_STATUS)
    template = models.FileField(_('Template'), 
    default="document_template.html".format(settings.MEDIA_URL), 
    upload_to = 'media', blank=True)

    def __str__(self):
        return self.get_name()

    def get_name(self):
        if self.short_name:
            return str(self.short_name)
        else:
            return str(self.name)

    def get_payment_status(self):
        if self.track_payment == 1:
            return _("Yes")
        else:
            return _("No")
    
    def get_due_status(self):
        if self.track_due_date == 1:
            return _("Yes")
        else:
            return _("No")
    
    def get_stock_status(self):
        if self.modify_stock == 1:
            return _("Yes")
        else:
            return _("No")

    def get_absolute_url(self):
        return reverse('document_details', kwargs={'slug': self.slug})

    def save(self, *args, **kwargs): # new
        if not self.slug:
            self.slug = slugify(self.name)
        return super().save(*args, **kwargs)

    class Meta:
        ordering = ("name",)


class Invoicing(models.Model):

    DELIVERED = 1
    NOT_DELIVERED = 0

    DELIVERED_STATUS = ((DELIVERED, _('Delivered')), (NOT_DELIVERED, _('Not delivered')))
    
    name =  models.CharField(_('Name'), max_length=50, unique=True)
    document =  models.ForeignKey(Document, verbose_name=_('Document'), on_delete=models.PROTECT)
    number = models.IntegerField(default=0)
    slug = models.SlugField(unique=True, null=False, editable=False)
    payment_method = models.ForeignKey(PaymentMethod, on_delete=models.PROTECT, default=1, verbose_name=_('Payment method'))
    payment_term = models.ForeignKey(PaymentTerm, on_delete=models.PROTECT, default=1, verbose_name=_('Payment term'))
    costumer = models.ForeignKey(verbose_name=_('Costumer'), to=Costumer, on_delete=models.PROTECT, default=1)
    date = models.DateTimeField(_('Date'), default=timezone.now)
    due_date = models.DateTimeField(_('Due Date'), 
    default=datetime.datetime.now() + datetime.timedelta(days=30))
    warehouse = models.ForeignKey(Warehouse, on_delete=models.PROTECT, default=1, verbose_name=_('Warehouse'))
    credit = models.DecimalField(_('Credit'), max_digits=18, decimal_places=6, default=0, blank=True)
    debit = models.DecimalField(_('Debit'), max_digits=18, decimal_places=6, default=0, blank=True)
    total = models.DecimalField(_('Total'), max_digits=18, decimal_places=6, default=0, blank=True)
    total_tax = models.DecimalField(_('Total Tax'), max_digits=18, decimal_places=6, default=0, blank=True)
    subtotal = models.DecimalField(_('Subtotal'), max_digits=18, decimal_places=6, default=0, blank=True)
    total_discount = models.DecimalField(_('Total Discount'), max_digits=18, decimal_places=6, default=0, blank=True)
    paid_status = models.IntegerField(_('Paid Status'), default=0)
    delivered_status = models.IntegerField(_('Delivered Status'), default=0)
    finished_status = models.IntegerField(_('Finished Status'), default=0)
    active_status = models.IntegerField(_('Active Status'), default=1)
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

    def is_finished(self):
        if self.finished_status == 1:
            return True
        else:
            return False
        
    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('invoice_details', kwargs={'slug': self.slug})

    def save(self, *args, **kwargs): # new
        invoice = '{} {}'.format(str(self.document), self.number)
        self.name = invoice

        if not self.slug:
            self.slug = slugify(invoice)
        return super().save(*args, **kwargs)

    class Meta:
        ordering = ('-name',)


class Receipt(models.Model):
    name = models.CharField(_('Name'), max_length=50, unique=True)
    number = models.IntegerField(unique=True, default=0)
    costumer = models.ForeignKey(Costumer, on_delete=models.PROTECT, default=1, verbose_name=_('Costumer'))
    slug = models.SlugField(unique=True, null=False, editable=False)
    notes = models.TextField(_('Notes'), blank=True)
    date_created = models.DateTimeField(editable=False, default=timezone.now)
    date_modified = models.DateTimeField(editable=False, default=timezone.now)
    created_by = models.ForeignKey(User, on_delete=models.PROTECT, related_name="+")
    modified_by = models.ForeignKey(User, on_delete=models.PROTECT, related_name="+")
    active_status = models.IntegerField(_('Active status'), default=1, blank=True)
    finished_status = models.IntegerField(_('Finished status'), default=0, blank=True)
    
    def is_finished(self):
        if self.finished_status == 1:
            return True
        else:
            return False

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('receipt_details', kwargs={'slug': self.slug})

    class Meta:
        ordering = ('-name',)


class Files(models.Model):
    file = models.ImageField(_('Add File'), 
    default="{}default.jpg".format(settings.MEDIA_URL), 
    upload_to = 'media', blank=True)
    receipt = models.ForeignKey(Receipt, on_delete=models.PROTECT)


class PaymentType(models.Model):
    name = models.CharField(max_length=255, unique=True)
    slug = models.SlugField(unique=True, null=False, editable=False)
    amount = models.DecimalField(max_digits=18, decimal_places=6, default=0)
    notes = models.CharField(max_length=255, blank=True)
    receipt = models.ForeignKey(Receipt, on_delete=models.PROTECT)

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('payment_type_details', kwargs={'slug': self.slug})

    def save(self, *args, **kwargs): # new
        if not self.slug:
            self.slug = slugify(self.name)
        return super().save(*args, **kwargs)

    class Meta:
        ordering = ("name",)
    

class AbstractInvoice(models.Model):
    DELIVERED = 1
    NOT_DELIVERED = 0

    DELIVERED_STATUS = ((DELIVERED, _('Delivered')), (NOT_DELIVERED, _('Not delivered')))

    name =  models.CharField(_('Name'), max_length=50, unique=True)
    number = models.IntegerField(unique=True)
    slug = models.SlugField(unique=True, null=False, editable=False)
    payment_method = models.ForeignKey(PaymentMethod, on_delete=models.PROTECT, default=1, verbose_name=_('Payment method'))
    payment_term = models.ForeignKey(PaymentTerm, on_delete=models.PROTECT, default=1, verbose_name=_('Payment term'))
    costumer = models.ForeignKey(verbose_name=_('Costumer'), to=Costumer, on_delete=models.PROTECT, default=1)
    date = models.DateTimeField(_('Invoice Date'), default=timezone.now)
    due_date = models.DateTimeField(_('Due Date'), 
    default=datetime.datetime.now() + datetime.timedelta(days=30))
    warehouse = models.ForeignKey(Warehouse, on_delete=models.PROTECT, default=1, verbose_name=_('Warehouse'))
    paid_status = models.IntegerField(default=0)
    delivered_status = models.IntegerField(default=0)
    finished_status = models.IntegerField(default=0)
    active_status = models.IntegerField(default=1)
    notes = models.TextField(_('Private Notes'), blank=True)
    public_notes = models.TextField(_('Public Notes'), blank=True)
    date_created = models.DateTimeField(editable=False, default=timezone.now)
    date_modified = models.DateTimeField(editable=False, default=timezone.now)
    created_by = models.ForeignKey(User, on_delete=models.PROTECT, related_name="+", default=1)
    modified_by = models.ForeignKey(User, on_delete=models.PROTECT, related_name="+", default=1)
    credit = models.DecimalField(max_digits=18, decimal_places=6, default=0, blank=True)
    debit = models.DecimalField(max_digits=18, decimal_places=6, default=0, blank=True)
    total = models.DecimalField(max_digits=18, decimal_places=6, default=0, blank=True)
    total_tax = models.DecimalField(max_digits=18, decimal_places=6, default=0, blank=True)
    subtotal = models.DecimalField(max_digits=18, decimal_places=6, default=0, blank=True)
    total_discount = models.DecimalField(max_digits=18, decimal_places=6, default=0, blank=True)
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

    def is_finished(self):
        if self.finished_status == 1:
            return True
        else:
            return False
        
    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('invoice_details', kwargs={'slug': self.slug})

    def save(self, *args, **kwargs): # new
        invoice = '{} {}'.format(_('Invoice'), self.number)
        self.name = invoice

        if not self.slug:
            self.slug = slugify(invoice)
        return super().save(*args, **kwargs)

    class Meta:
        ordering = ('-name',)
        abstract = True


class Invoice(models.Model):
    DELIVERED = 1
    NOT_DELIVERED = 0

    DELIVERED_STATUS = ((DELIVERED, _('Delivered')), (NOT_DELIVERED, _('Not delivered')))

    name =  models.CharField(_('Name'), max_length=50, unique=True)
    number = models.IntegerField(unique=True)
    slug = models.SlugField(unique=True, null=False, editable=False)
    payment_method = models.ForeignKey(PaymentMethod, on_delete=models.PROTECT, default=1, verbose_name=_('Payment method'))
    payment_term = models.ForeignKey(PaymentTerm, on_delete=models.PROTECT, default=1, verbose_name=_('Payment term'))
    costumer = models.ForeignKey(verbose_name=_('Costumer'), to=Costumer, on_delete=models.PROTECT, default=1)
    date = models.DateTimeField(_('Invoice Date'), default=timezone.now)
    due_date = models.DateTimeField(_('Due Date'), 
    default=datetime.datetime.now() + datetime.timedelta(days=30))
    warehouse = models.ForeignKey(Warehouse, on_delete=models.PROTECT, default=1, verbose_name=_('Warehouse'))
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
    credit = models.DecimalField(max_digits=18, decimal_places=6, default=0, blank=True)
    debit = models.DecimalField(max_digits=18, decimal_places=6, default=0, blank=True)
    total = models.DecimalField(max_digits=18, decimal_places=6, default=0, blank=True)
    total_tax = models.DecimalField(max_digits=18, decimal_places=6, default=0, blank=True)
    subtotal = models.DecimalField(max_digits=18, decimal_places=6, default=0, blank=True)
    total_discount = models.DecimalField(max_digits=18, decimal_places=6, default=0, blank=True)
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

    def is_finished(self):
        if self.finished_status == 1:
            return True
        else:
            return False
        
    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('invoice_details', kwargs={'slug': self.slug})

    def save(self, *args, **kwargs): # new
        invoice = '{} {}'.format(_('Invoice'), self.number)
        self.name = invoice

        if not self.slug:
            self.slug = slugify(invoice)
        return super().save(*args, **kwargs)

    class Meta:
        ordering = ('-name',)

class ProductReturn(AbstractInvoice):
    invoicing = models.ForeignKey(Invoicing, on_delete=models.PROTECT, 
    verbose_name=_('Select Invoice'), related_name="invoice_model", default=1)


class InvoiceItem(models.Model):
    invoice = models.ForeignKey(Invoice, on_delete=models.PROTECT)
    product = models.ForeignKey(Product, on_delete=models.PROTECT)
    tax = models.DecimalField(max_digits=4, decimal_places=2, default=0)
    discount = models.DecimalField(max_digits=4, decimal_places=2, default=0)
    price = models.DecimalField(max_digits=18, decimal_places=6, default=0)
    quantity = models.DecimalField(max_digits=18, decimal_places=6, default=0)
    tax_total = models.DecimalField(max_digits=18, decimal_places=6, default=0)
    discount_total = models.DecimalField(max_digits=18, decimal_places=6, default=0)
    sub_total = models.DecimalField(max_digits=18, decimal_places=6, default=0)
    total = models.DecimalField(max_digits=18, decimal_places=6, default=0)
    
    @property
    def get_line_total(self):
        return self.quantity * self.price

    def __str__(self):
        return '{} {}'.format(self.invoice, self.product)
    
    def save(self, *args, **kwargs): # new
        
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


class ReceiptInvoice(models.Model):
    invoice = models.ForeignKey(Invoice, on_delete=models.PROTECT)
    receipt = models.ForeignKey(Receipt, on_delete=models.PROTECT)
    debit = models.DecimalField(max_digits=18, decimal_places=6, default=0)
    remaining = models.DecimalField(max_digits=18, decimal_places=6, default=0)
    paid = models.DecimalField(max_digits=18, decimal_places=6, default=0)

    def __str__(self):
        return "{}".format(self.invoice, self.receipt)
    
    class Meta:
        verbose_name = _('Receipt Invoice')
        verbose_name_plural = _('Receipt Invoices')
        unique_together = ['receipt', 'invoice']


class AbstractInvoicingItem(models.Model):
    product = models.ForeignKey(Product, on_delete=models.PROTECT)
    tax = models.DecimalField(max_digits=4, decimal_places=2, default=0)
    discount = models.DecimalField(max_digits=4, decimal_places=2, default=0)
    price = models.DecimalField(max_digits=18, decimal_places=6, default=0)
    quantity = models.DecimalField(max_digits=18, decimal_places=6, default=0)
    tax_total = models.DecimalField(max_digits=18, decimal_places=6, default=0)
    discount_total = models.DecimalField(max_digits=18, decimal_places=6, default=0)
    sub_total = models.DecimalField(max_digits=18, decimal_places=6, default=0)
    total = models.DecimalField(max_digits=18, decimal_places=6, default=0)
    
    @property
    def get_line_total(self):
        return self.quantity * self.price

    def __str__(self):
        return '{} {}'.format(self.invoicing, self.product)
    
    def save(self, *args, **kwargs): # new
        
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

    class Meta:
        abstract = True

class InvoicingItem(models.Model):
    invoicing = models.ForeignKey(Invoicing, on_delete=models.PROTECT)
    product = models.ForeignKey(Product, on_delete=models.PROTECT)
    tax = models.DecimalField(max_digits=4, decimal_places=2, default=0)
    discount = models.DecimalField(max_digits=4, decimal_places=2, default=0)
    price = models.DecimalField(max_digits=18, decimal_places=6, default=0)
    quantity = models.DecimalField(max_digits=18, decimal_places=6, default=0)
    tax_total = models.DecimalField(max_digits=18, decimal_places=6, default=0)
    discount_total = models.DecimalField(max_digits=18, decimal_places=6, default=0)
    sub_total = models.DecimalField(max_digits=18, decimal_places=6, default=0)
    total = models.DecimalField(max_digits=18, decimal_places=6, default=0)
    
    @property
    def get_line_total(self):
        return self.quantity * self.price

    def __str__(self):
        return '{} {}'.format(self.invoicing, self.product)
    
    def save(self, *args, **kwargs): # new
        
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

class ProductReturnItem(AbstractInvoicingItem):
    product_return = models.ForeignKey(ProductReturn, on_delete=models.PROTECT)

class DocumentPayment(models.Model):
    invoicing = models.ForeignKey(Invoicing, on_delete=models.PROTECT)
    payment_method = models.ForeignKey(PaymentMethod, on_delete=models.PROTECT)
    amount = models.DecimalField(max_digits=18, decimal_places=6, default=0)
    notes = models.CharField(max_length=255, blank=True)
    file = models.ImageField(_('Add File'), 
    upload_to = 'media', blank=True)

    def __str__(self):
        return '{} - {}'.format(str(self.invoicing), str(self.payment_method))


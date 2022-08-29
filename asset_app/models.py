# -*- coding: utf-8 -*-
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
from warehouse.models import Warehouse


ACTIVE = 1
DEACTIVATED  = 0

STATUSES = ((ACTIVE, _('Active')), (DEACTIVATED , _('Inactive')))


class Settings(models.Model):
    name = models.CharField(_('Costumer Name'), max_length=100, unique=True)
    vat = models.CharField(_('VAT number'), max_length=15, blank=True)
    slug = models.SlugField(unique=True, null=False, editable=False)
    address = models.CharField(_('Address'), blank=True, max_length=255)
    cell = models.CharField(_('Cell'), blank=True, max_length=255)
    cell_2 = models.CharField(_('Cell 2'), blank=True, max_length=255)
    phone = models.CharField(_('Telephone'), blank=True, max_length=255)
    fax = models.CharField(_('Fax'), blank=True, max_length=255)
    email = models.EmailField(_('Email'), blank=True)
    website = models.CharField(_('Web Site'), max_length=255, blank=True)
    logo = models.ImageField(_('Logo'), max_length=255, blank=True)
    logo_square = models.ImageField(_('Logo Square'), max_length=255, blank=True)
    notes = models.TextField(_('Notes'), blank=True)
    date_created = models.DateTimeField(editable=False, default=timezone.now)
    date_modified = models.DateTimeField(editable=False, default=timezone.now)
    created_by = models.ForeignKey(User, on_delete=models.PROTECT, related_name="+")
    modified_by = models.ForeignKey(User, on_delete=models.PROTECT, related_name="+")

    def get_absolute_url(self):
        return reverse('maintenance_details', kwargs={'slug': self.slug})

    def save(self, *args, **kwargs): # new
        if not self.slug:
            self.slug = slugify(self.name)
        return super().save(*args, **kwargs)

    class Meta:
        verbose_name = "Settings"
        verbose_name_plural = "Settings"
        ordering = ("name",)
    
    def __str__(self):
        return self.name


class Maintenance(models.Model):
    
    ROUTINE = 'Routine'
    PREVENTIVE = 'Preventive'
    CORRECTIVE = 'Corrective'
    PREDECTIVE = 'Predective'

    MAINTENANCE_CHOICES = (
        (ROUTINE, 'Routine'), 
        (PREVENTIVE, 'Preventive'), 
        (CORRECTIVE, 'Corrective'), 
        (PREDECTIVE, 'Predective'), 
    )

    HOURS = 'Hours'
    DAYS = 'Days'
    MONTHS = 'Months'
    KM = 'KM'

    MAINTENANCE_SCHEDULE = (
        (HOURS, 'Hours'), (DAYS, 'Days'), (MONTHS, 'Months'), 
        (KM, 'KM\'s'), 
    )

    name = models.CharField(max_length=50)
    type = models.CharField(choices=MAINTENANCE_CHOICES, default=ROUTINE, max_length=15)
    slug = models.SlugField(unique=True, null=False, editable=False)
    schedule = models.CharField(choices=MAINTENANCE_SCHEDULE, default=HOURS, max_length=10)
    frequency = models.PositiveIntegerField(default=0)
    time_allocated = models.FloatField(default=0)
    time_schedule = models.CharField(choices=MAINTENANCE_SCHEDULE, default=HOURS, max_length=10)
    active_status = models.IntegerField(_('Status'), choices=STATUSES, default=ACTIVE)
    notes = models.TextField(_('Notes'), blank=True)
    date_created = models.DateTimeField(editable=False, 
    default=timezone.now)
    date_modified = models.DateTimeField(editable=False, 
    default=timezone.now)
    created_by = models.ForeignKey(User, on_delete=models.PROTECT, related_name="+")
    modified_by = models.ForeignKey(User, on_delete=models.PROTECT, related_name="+")
    
    def get_absolute_url(self):
        return reverse('maintenance_details', kwargs={'slug': self.slug})

    def save(self, *args, **kwargs): # new
        if not self.slug:
            self.slug = slugify('{}-{}'.format(self.name, self.type))
        return super().save(*args, **kwargs)

    class Meta:
        verbose_name = "Maintenance"
        verbose_name_plural = "Maintenances"
        ordering = ("name",)
        unique_together = ('name', 'type',)

    def __str__(self):
        return '{} ({})'.format(self.name, self.type)


class Component(models.Model):
    component_no = models.PositiveIntegerField(_('System no'), unique=True)
    name = models.CharField(_('Component Name'), max_length=100, unique=True)
    slug = models.SlugField(unique=True, null=False, editable=False)
    manufacturer = models.CharField(_('Manufacturer'), max_length=100, blank=True)
    stock_code = models.CharField(_('Stock Code'), max_length=100, blank=True)
    maintenance = models.ForeignKey(Maintenance, on_delete=models.PROTECT)
    image = models.ImageField(_('Image'), default="{}default.jpg".format(settings.MEDIA_URL), upload_to = 'media')
    active_status = models.IntegerField(_('Status'), choices=STATUSES, default=ACTIVE)
    notes = models.TextField(_('Notes'), blank=True)
    date_created = models.DateTimeField(editable=False, default=timezone.now)
    date_modified = models.DateTimeField(editable=False, default=timezone.now)
    created_by = models.ForeignKey(User, on_delete=models.PROTECT, related_name="+")
    modified_by = models.ForeignKey(User, on_delete=models.PROTECT, related_name="+")

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('component_details', kwargs={'slug': self.slug})

    def save(self, *args, **kwargs): # new
        if not self.slug:
            self.slug = slugify(self.name)
        return super().save(*args, **kwargs)

    class Meta:
        verbose_name = "Component"
        verbose_name_plural = "Components"
        ordering = ("name",)


class Costumer(models.Model):
    TYPE_CHOICES = (("Governmental", _("Governmental")), ("Large Company",
    _("Large Company")), ("Medium Company", _("Medium Company")),
    ("Small Company", _("Small Company")), ("Individual Company", _("Individual Company")),
    ("Other", _("Other")))

    name = models.CharField(_('Costumer Name'), 
    help_text=_('Name of the Costumer, Department, etc'), max_length=100, unique=True)
    country = models.CharField(_('Country'), max_length=100, blank=True)
    province = models.CharField(_('Province/State'), max_length=100, blank=True)
    city = models.CharField(_('City'), max_length=100, blank=True)
    zip = models.CharField(_('Zip Code'), max_length=100, blank=True)
    parent = models.IntegerField(_('Parent Costumer'), 
    help_text=_('Choose Parent Costumer'), default=0)
    slug = models.SlugField(unique=True, null=False, editable=False)
    address = models.CharField(blank=True, max_length=255)
    phone = models.CharField(_('Phone'), blank=True, max_length=255)
    fax = models.CharField(_('Fax'), blank=True, max_length=255)
    mobile = models.CharField(_('Mobile'), blank=True, max_length=255)
    capital = models.DecimalField(_("Capital"), max_digits=18, decimal_places=6, default=0)
    current_credit = models.DecimalField(max_digits=18, decimal_places=6, default=0)
    max_credit = models.DecimalField(max_digits=18, decimal_places=6, default=0, blank=True)
    max_debit = models.DecimalField(max_digits=18, decimal_places=6, default=0, blank=True)
    credit = models.DecimalField(max_digits=18, decimal_places=6, default=0, blank=True)
    debit = models.DecimalField(max_digits=18, decimal_places=6, default=0, blank=True)
    email = models.CharField(max_length = 254, blank=True)
    website = models.CharField(max_length = 254, blank=True)
    is_supplier = models.IntegerField(default=0)
    is_costumer = models.IntegerField(default=0)
    active_status = models.IntegerField(_('Status'), choices=STATUSES, default=ACTIVE)
    notes = models.TextField(_('Notes'), blank=True)
    date_created = models.DateTimeField(editable=False, 
    default=timezone.now)
    date_modified = models.DateTimeField(editable=False, 
    default=timezone.now)
    created_by = models.ForeignKey(User, on_delete=models.PROTECT, related_name="+")
    modified_by = models.ForeignKey(User, on_delete=models.PROTECT, related_name="+")
    warehouse = models.ForeignKey(Warehouse, verbose_name=_("Default Warehouse"), 
    on_delete=models.PROTECT, null=True, blank=True)
    type = models.CharField(_("Company Type"), max_length=20, choices=TYPE_CHOICES,
    default=TYPE_CHOICES[3][1])
    vat = models.CharField(_("VAT Number"), max_length=15, blank=True)


    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('costumer_details', kwargs={'slug': self.slug})

    def save(self, *args, **kwargs): # new
        if not self.slug:
            self.slug = slugify(self.name)
        return super().save(*args, **kwargs)

    class Meta:
        ordering = ("name",)
        verbose_name_plural = "Costumers"


class Group(models.Model):
    name = models.CharField(_('Group'), max_length=50, unique=True)
    slug = models.SlugField(unique=True, null=False, editable=False)
    notes = models.TextField(_('Notes'), blank=True)
    date_created = models.DateTimeField(editable=False, 
    default=timezone.now)
    date_modified = models.DateTimeField(editable=False, 
    default=timezone.now)
    created_by = models.ForeignKey(User, on_delete=models.PROTECT, related_name="+")
    modified_by = models.ForeignKey(User, on_delete=models.PROTECT, related_name="+")

    def get_absolute_url(self):
        return reverse('group_details', kwargs={'slug': self.slug})

    def __str__(self):
        return self.name
    
    def save(self, *args, **kwargs): # new
        if not self.slug:
            self.slug = slugify(self.name)
        return super().save(*args, **kwargs)


class System(models.Model):
    name = models.CharField(_('System'), max_length=50, unique=True)
    group = models.ForeignKey(Group, on_delete=models.PROTECT)
    slug = models.SlugField(unique=True, null=False, editable=False)
    notes = models.TextField(_('Notes'), blank=True)
    date_created = models.DateTimeField(editable=False, 
    default=timezone.now)
    date_modified = models.DateTimeField(editable=False, 
    default=timezone.now)
    created_by = models.ForeignKey(User, on_delete=models.PROTECT, related_name="+")
    modified_by = models.ForeignKey(User, on_delete=models.PROTECT, related_name="+")

    def get_absolute_url(self):
        return reverse('system_details', kwargs={'slug': self.slug})

    def __str__(self):
        return self.name
    
    def save(self, *args, **kwargs): # new
        if not self.slug:
            self.slug = slugify(self.name)
        return super().save(*args, **kwargs)


class Type(models.Model):
    name = models.CharField(_('Type'), max_length=50, unique=True)
    system = models.ForeignKey(System, on_delete=models.PROTECT)
    slug = models.SlugField(unique=True, null=False, editable=False)
    notes = models.TextField(_('Notes'), blank=True)
    date_created = models.DateTimeField(editable=False, 
    default=timezone.now)
    date_modified = models.DateTimeField(editable=False, 
    default=timezone.now)
    created_by = models.ForeignKey(User, on_delete=models.PROTECT, related_name="+")
    modified_by = models.ForeignKey(User, on_delete=models.PROTECT, related_name="+")

    def get_absolute_url(self):
        return reverse('type_details', kwargs={'slug': self.slug})

    def __str__(self):
        return self.name
    
    def save(self, *args, **kwargs): # new
        if not self.slug:
            self.slug = slugify(self.name)
        return super().save(*args, **kwargs)


class SubType(models.Model):
    name = models.CharField(_('Subtype'), max_length=50, unique=True)
    type = models.ForeignKey(Type, on_delete=models.PROTECT)
    slug = models.SlugField(unique=True, null=False, editable=False)
    notes = models.TextField(_('Notes'), blank=True)
    date_created = models.DateTimeField(editable=False, 
    default=timezone.now)
    date_modified = models.DateTimeField(editable=False, 
    default=timezone.now)
    created_by = models.ForeignKey(User, on_delete=models.PROTECT, related_name="+")
    modified_by = models.ForeignKey(User, on_delete=models.PROTECT, related_name="+")

    def get_absolute_url(self):
        return reverse('subtype_details', kwargs={'slug': self.slug})

    def __str__(self):
        return self.name
    
    def save(self, *args, **kwargs): # new
        if not self.slug:
            self.slug = slugify(self.name)
        return super().save(*args, **kwargs)


    class Meta(object):
        verbose_name_plural = "Subtypes"


class Vendor(models.Model):

    name = models.CharField(_('Vendor Name'), 
    help_text=_('Name of the Vendor, Department, etc'),max_length=100, unique=True)
    slug = models.SlugField(unique=True, null=False, editable=False)
    address = models.CharField(blank=True, max_length=255)
    contacts = models.CharField(blank=True, max_length=255)
    manager = models.CharField(max_length=100, blank=True)
    email = models.EmailField(max_length = 254, blank=True)
    active_status = models.IntegerField(_('Status'), choices=STATUSES, default=ACTIVE)
    notes = models.TextField(_('Notes'), blank=True)
    date_created = models.DateTimeField(editable=False, 
    default=timezone.now)
    date_modified = models.DateTimeField(editable=False, 
    default=timezone.now)
    created_by = models.ForeignKey(User, on_delete=models.PROTECT, related_name="+")
    modified_by = models.ForeignKey(User, on_delete=models.PROTECT, related_name="+")


    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('vendor_details', kwargs={'slug': self.slug})

    def save(self, *args, **kwargs): # new
        if not self.slug:
            self.slug = slugify(self.name)
        return super().save(*args, **kwargs)

    class Meta:
        ordering = ("name",)
        verbose_name_plural = "Vendors"


class Allocation(models.Model):
   
    GOOD = 'Good'
    BROKEN = 'Broken'
    
    STATUS = ((GOOD, 'Good'), (BROKEN, 'Broken'),)

    allocation_no = models.PositiveIntegerField(_("Allocation No."), unique=True) # validators=[RegexValidator(r'^[0-9]{9}$')]
    component = models.ForeignKey(Component,on_delete=models.PROTECT, verbose_name= _('component Name'))
    vendor = models.ForeignKey(Vendor, on_delete=models.PROTECT, verbose_name= _('Vendor Name'))
    costumer = models.ForeignKey(Costumer, on_delete=models.PROTECT)
    serial_number = models.CharField(_('Component Serial No.'), max_length=50, unique=True)
    status = models.CharField(_('Status'), max_length=15, choices=STATUS, default=GOOD)
    image = models.ImageField(_('Image'), default="{}default.jpg".format(settings.MEDIA_URL), 
    upload_to = 'media', blank=True)
    slug = models.SlugField(unique=True, null=False, editable=False)
    purchase_amount = models.DecimalField(default=0, max_digits=9, decimal_places=2)
    date_purchased = models.DateTimeField(default=timezone.now)
    date_allocated = models.DateTimeField(default=timezone.now)
    depreciation = models.FloatField(_('Depreciation %'), default=0)
    start_value_hours = models.FloatField(_('Start Value (Hours)'), default=0)
    start_value_years = models.FloatField(_('Start Value (Years)'), default=0)
    start_value_milliege = models.FloatField(_('Start Value (KM)'), default=0)
    garrantee_value_hours = models.FloatField(_('Warrantee Value (Hours)'), default=0)
    garrantee_value_years = models.FloatField(_('Warrantee Value (Years)'), default=0)
    garrantee_milliege = models.FloatField(_('Warrantee Milliege (KM)'), default=0)
    end_of_life_hours = models.FloatField(_('End of Life (Hours)'), default=0)
    end_of_life_years = models.FloatField(_('End of Life (Years)'),default=0)
    end_of_life_milliege = models.FloatField(_('End of Life (KM)'),default=0)
    warn_before_hours = models.FloatField(_('Warn Before (Hours)'), default=0)
    warn_before_years = models.FloatField(_('Warn Before (Years)'), default=0)
    warn_before_milliege = models.FloatField(_('Warn Before (KM)'), default=0)
    group = models.ForeignKey(Group, on_delete=models.PROTECT)
    system = models.ForeignKey(System, on_delete=models.PROTECT)
    type = models.ForeignKey(Type, on_delete=models.PROTECT)
    subtype = models.ForeignKey(SubType, on_delete=models.PROTECT)
    notes = models.TextField(_('Notes'), blank=True)
    active_status = models.IntegerField(_('Status'), choices=STATUSES, default=ACTIVE)
    date_created = models.DateTimeField(editable=False, 
    default=timezone.now)
    date_modified = models.DateTimeField(editable=False, 
    default=timezone.now)
    created_by = models.ForeignKey(User, on_delete=models.PROTECT, related_name="+")
    modified_by = models.ForeignKey(User, on_delete=models.PROTECT, related_name="+")
    qrcode = models.ImageField(_('QrCode'), upload_to = 'media', blank=True)

    def __str__(self):
        return str('{} - {}'.format(self.allocation_no, self.component))

    def get_absolute_url(self):
        return reverse('allocation_details', kwargs={'slug': self.slug})

    def save(self, *args, **kwargs): # new
        if not self.slug:
            self.slug = slugify('{}-{}'.format(self.allocation_no, self.component))
        return super().save(*args, **kwargs)

    class Meta:
        verbose_name_plural = "Allocations"
        ordering = ("-date_allocated",)


class WorkOrder(models.Model):
    
    PENDING = 'Pending'
    INPROGRESS = 'InProgress'
    ABANDONED = 'Abandoned'
    FINISHED = 'Finished'

    LOW = 'LOW'
    MEDIUM = 'MEDIUM'
    HIGH = 'HIGH'

    PROGRESS_STATUSES = ((PENDING, _('Pending')), (INPROGRESS, _('InProgress')),
    (FINISHED, _('Finished')), (ABANDONED, _('Abandoned')))

    PRIORITY = ((LOW, _('Low')), (MEDIUM, _('Medium')), (HIGH, _('High')))

    order = models.PositiveIntegerField(_('Order Number'), unique=True)
    priority = models.CharField(_('Priority'), max_length=10, choices=PRIORITY, default=LOW)
    slug = models.SlugField(unique=True, null=False, editable=False)
    component = models.ManyToManyField(Allocation, related_name='workorders', 
    verbose_name=_('Component'))
    responsible = models.ForeignKey(User, on_delete=models.PROTECT, verbose_name=_('Person in Charge'))
    start = models.DateTimeField(_("Start date"), default=timezone.now)
    end = models.DateTimeField(_("End date"), default=timezone.now)
    warn_after = models.DateTimeField(_('Warn After'), default=timezone.now) 
    status = models.CharField(_('Progress'), max_length=15, choices=PROGRESS_STATUSES, default=PENDING, blank=True)
    progress = models.DecimalField(_('Work Progress (%)'), max_digits=5, decimal_places=2, default=0)
    notes = models.TextField(_('Notes'), blank=True)
    active_status = models.IntegerField(_('Active Status'), choices=STATUSES, default=ACTIVE)
    date_created = models.DateTimeField(editable=False, 
    default=timezone.now)
    date_modified = models.DateTimeField(editable=False, 
    default=timezone.now)
    created_by = models.ForeignKey(User, on_delete=models.PROTECT, related_name="+")
    modified_by = models.ForeignKey(User, on_delete=models.PROTECT, related_name="+")

    @property
    def is_overdue(self):
        if self.end < datetime.datetime.now() and self.status in (self.PENDING, self.INPROGRESS):
            return True
        return False
    
    @property
    def is_complete(self):
        if self.progress == 100 or self.status == self.FINISHED:
            return True
        return False
    
    @property
    def is_pending(self):
        if self.status == self.PENDING and not self.is_overdue:
            return True
        return False

    @property
    def is_progress(self):
        if self.status == self.INPROGRESS and not self.is_overdue:
            return True
        return False

    def __str__(self):
        return "%s (%s)" % (
        self.order,
        ", ".join(component.name for component in self.components.all()),
        )

    def get_absolute_url(self):
        return reverse('work_details', kwargs={'slug': self.slug})

    def save(self, *args, **kwargs): # new
        if not self.slug:
            self.slug = self.order
        return super().save(*args, **kwargs)

    class Meta:
        verbose_name_plural = "Work Orders"
        verbose_name = "Work Order"
        ordering = ("-start",)


# Maintenance Action
class Action(models.Model):
   
    name = models.CharField(_('Name'), max_length=50, unique=True)
    maintenance = models.ForeignKey(Maintenance, on_delete=models.PROTECT)
    slug = models.SlugField(unique=True, null=False, editable=False)
    notes = models.TextField(_('Notes'), blank=True)
    active_status = models.IntegerField(_('Status'), choices=STATUSES, default=ACTIVE)
    date_created = models.DateTimeField(editable=False, 
    default=timezone.now)
    date_modified = models.DateTimeField(editable=False, 
    default=timezone.now)
    created_by = models.ForeignKey(User, on_delete=models.PROTECT, related_name="+")
    modified_by = models.ForeignKey(User, on_delete=models.PROTECT, related_name="+")
    
    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('action_details', kwargs={'slug': self.slug})

    def save(self, *args, **kwargs): # new
        if not self.slug:
            self.slug = slugify(self.name)
        return super().save(*args, **kwargs)

    class Meta:
        ordering = ("name",)


class Item(models.Model):
    cm = 'Cm'
    kg = 'Kg'
    gb = 'Gb'
    mb = 'Mb'
    piece = 'Piece'
    m3 = 'M³'
    km = 'Km'
    l = 'L'
    g = 'G'

    UNITY_CHOICES = ((cm, _('Cm')), (kg, _('Kg')), (l, _('L')),(gb, _('Gb')), 
    (mb, _('Mb')), (piece, _('Piece')), (m3, _('M3')), (km, _('Km')), (g, _('G')))

    name = models.CharField(_('Name'), max_length=50, unique=True)
    slug = models.SlugField(unique=True, null=False, editable=False)
    quantity = models.DecimalField(_('Quantity'), decimal_places=2, max_digits=9)
    cost = models.DecimalField(_('Cost'), decimal_places=2, max_digits=9, default=0)
    unit = models.CharField(_('Unit'), max_length=10, choices=UNITY_CHOICES, default=piece)
    active_status = models.IntegerField(_('Status'), choices=STATUSES, default=ACTIVE)
    notes = models.TextField(_('Notes'), blank=True)
    date_created = models.DateTimeField(editable=False, 
    default=timezone.now)
    date_modified = models.DateTimeField(editable=False, 
    default=timezone.now)
    created_by = models.ForeignKey(User, on_delete=models.PROTECT, related_name="+")
    modified_by = models.ForeignKey(User, on_delete=models.PROTECT, related_name="+")
    
    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('item_details', kwargs={'slug': self.slug})

    def save(self, *args, **kwargs): # new
        if not self.slug:
            self.slug = slugify(self.name)
        return super().save(*args, **kwargs)

    class Meta:
        ordering = ("name",)


class MaintenanceItem(models.Model):
    
    maintenance = models.ForeignKey(Maintenance, on_delete=models.PROTECT)
    item = models.ForeignKey(Item, on_delete=models.PROTECT)
    quantity = models.DecimalField(_('Quantity'), decimal_places=2, max_digits=9, default=0)
    cost = models.DecimalField(_('Cost'), decimal_places=2, max_digits=9, default=0)
    active_status = models.IntegerField(_('Status'), choices=STATUSES, default=ACTIVE)

    def __str__(self):
        return '{} - {}'.format(self.maintenance, self.item)    

    class Meta:
        verbose_name_plural = "Maintenance Items"
        unique_together = [['maintenance', 'item']]



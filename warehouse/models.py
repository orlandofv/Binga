# -*- coding: utf-8 -*-
from django.db import models
from users.models import User
from django.urls import reverse
from django.template.defaultfilters import slugify # new
from django.utils.translation import ugettext_lazy as _
from django.utils import timezone

# Create your models here.

ACTIVE = 1
DEACTIVATED  = 0

STATUSES = ((ACTIVE, _('Active')), (DEACTIVATED , _('Inactive')))


class Warehouse(models.Model):
    
    OPEN = 'OPEN'
    CLOSE = 'CLOSE'

    OPEN_STATUS = ((OPEN, 'Open'), (CLOSE, 'Close'))

    name = models.CharField(max_length=25, unique=True)
    slug = models.SlugField(unique=True, null=False, editable=False)
    parent = models.IntegerField(default=0)
    description = models.TextField(blank=True)
    address = models.CharField(blank=True, max_length=255)
    contacts = models.CharField(max_length=255, blank=True)
    active_status = models.IntegerField(_('Active status'), choices=STATUSES, default=ACTIVE)
    open_status = models.CharField(max_length=25, choices=OPEN_STATUS, default=OPEN)
    notes = models.TextField(_('Notes'), blank=True)
    date_created = models.DateTimeField(editable=False, default=timezone.now)
    date_modified = models.DateTimeField(editable=False, default=timezone.now)
    created_by = models.ForeignKey(User, on_delete=models.PROTECT, related_name="+")
    modified_by = models.ForeignKey(User, on_delete=models.PROTECT, related_name="+")

    def get_parent(self):
        if self.parent in ("", 0, None):
            return '--'
        else:
            return Warehouse.objects.filter(id=self.parent).first()

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('warehouse_details', kwargs={'slug': self.slug})

    def save(self, *args, **kwargs): # new
        if not self.slug:
            self.slug = slugify(self.name)
        return super().save(*args, **kwargs)

    class Meta:
        ordering = ("name",)


class UserWarehouse(models.Model):
    user = models.ForeignKey(User, on_delete=models.PROTECT)
    warehouse = models.ForeignKey(Warehouse,verbose_name=_('Default Warehouse'), 
    on_delete=models.PROTECT, null=True)

    class Meta:
        unique_together = ['user', 'warehouse']


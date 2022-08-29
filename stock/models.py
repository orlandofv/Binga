# -*- coding: utf-8 -*-
from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.utils import timezone
from asset_app.models import Costumer

from users.models import User
from isis.models import Product
from warehouse.models import Warehouse


# Create your models here.
class Stock(models.Model):
    document = models.CharField(max_length=50)
    warehouse = models.ForeignKey(Warehouse, on_delete=models.PROTECT)
    product = models.ForeignKey(Product, on_delete=models.PROTECT)
    costumer = models.ForeignKey(Costumer, on_delete=models.PROTECT)
    quantity = models.DecimalField(max_digits=18, decimal_places=6, default=0)
    date_created = models.DateTimeField(editable=False, default=timezone.now)
    date_modified = models.DateTimeField(editable=False, default=timezone.now)
    created_by = models.ForeignKey(User, on_delete=models.PROTECT, related_name="+")
    modified_by = models.ForeignKey(User, on_delete=models.PROTECT, related_name="+")
    origin = models.CharField(max_length=20, default="Costumer Invoice")
    
    def __str__(self):
        return '{} - {}'.format(self.id , self.date_created)

    class Meta:
        ordering = ('-date_created',)



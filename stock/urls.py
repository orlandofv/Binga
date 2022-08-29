# -*- coding: utf-8 -*-
from django.conf import settings
from django.conf.urls.static import static

from django.urls import path
from .views import (stock_movement_view, stock_item_list_view, 
stock_summary_list_view)

app_name = 'stock'

urlpatterns = [
    path('stock/summary/', stock_summary_list_view, name='stock_summary_list'),
    path('stock/movement/', stock_movement_view, name='stock_movement'),
    path('stock/<slug:slug>/movements', stock_item_list_view, name='stock_item_list'),

]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)


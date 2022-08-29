# -*- coding: utf-8 -*-
from django.conf import settings
from django.conf.urls.static import static

from django.urls import path

from .views import (warehouse_create_view, warehouse_list_view, warehouse_update_view, warehouse_delete_view, warehouse_detail_view
)

app_name = 'warehouse'

urlpatterns = [
path('warehouses/new/', warehouse_create_view, name='warehouse_create'),
path('warehouses/', warehouse_list_view, name='warehouse_list'),
path('warehouses/<slug:slug>/update/', warehouse_update_view, name='warehouse_update'),
path('warehouses/delete/', warehouse_delete_view, name='warehouse_delete'),
path('warehouses/<slug:slug>/', warehouse_detail_view, name='warehouse_details'),
]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)


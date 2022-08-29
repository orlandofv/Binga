# -*- coding: utf-8 -*-
from django.conf import settings
from django.conf.urls.static import static

from django.urls import path
from .views import (invoice_list_view, invoice_create_view, invoice_update_view, invoice_delete_view, 
invoice_detail_view,  invoice_item_create_view, invoice_item_delete_view,
CostumerListView, CostumerCreateView, CostumerUpdateView, costumer_delete_view, 
CostumerDetailView, invoice_show,  costumer_receipt_create_view, CostumerReceiptListView, costumer_receipt_update_view, costumer_receipt_delete_view, 
costumer_receipt_detail_view, costumer_receipt_show, costumer_receipt_invoice_view)


app_name = 'costumer'

urlpatterns = [
    path('costumers/', CostumerListView.as_view(), name='costumer_list'),
    path('costumers/new/', CostumerCreateView.as_view(), name='costumer_create'),
    path('costumers/<pk>/update/', CostumerUpdateView.as_view(), name='costumer_update'),
    path('costumers/delete/', costumer_delete_view, name='costumer_delete'),
    path('costumers/<pk>/details', CostumerDetailView.as_view(), name='costumer_details'),
    path('costumer/invoices/new/', invoice_create_view, name='costumer_invoice_create'),
    path('costumer/invoices/', invoice_list_view, name='costumer_invoice_list'),
    path('costumer/invoices/<pk>/update/', invoice_update_view, name='costumer_invoice_update'),
    path('costumer/invoices/<pk>/show/', invoice_show, name='costumer_invoice_show'),
    path('costumer/invoices/delete/', invoice_delete_view, name='costumer_invoice_delete'),
    path('costumer/invoices/<pk>/', invoice_detail_view, name='costumer_invoice_details'),
    path('costumer/invoices/<pk>/items/', invoice_item_create_view, name='costumer_invoice_item_create'),
    path('costumer/invoices/items/delete/', invoice_item_delete_view, name='costumer_invoice_item_delete'),
    path('costumer/receipts/new/', costumer_receipt_create_view, name='costumer_receipt_create'),
    path('costumer/receipts/', CostumerReceiptListView.as_view(), name='costumer_receipt_list'),
    path('costumer/receipts/<pk>/update/', costumer_receipt_update_view, name='costumer_receipt_update'),
    path('costumer/receipts/delete/', costumer_receipt_delete_view, name='costumer_receipt_delete'),
    path('costumer/receipts/<pk>/items/', costumer_receipt_invoice_view, name='costumer_receipt_invoice'),
    path('costumer/receipts/<pk>/details/', costumer_receipt_detail_view, name='costumer_receipt_details'),
    path('costumer/receipts/<pk>/show/', costumer_receipt_show, name='costumer_receipt_show'),
    
]


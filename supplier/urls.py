# -*- coding: utf-8 -*-
from django.conf import settings
from django.conf.urls.static import static

from django.urls import path
from .views import (invoice_list_view, invoice_create_view, invoice_update_view, invoice_delete_view, 
invoice_detail_view,  invoice_item_create_view, invoice_item_delete_view,
SupplierListView, SupplierCreateView, SupplierUpdateView, supplier_delete_view, 
SupplierDetailView, invoice_show,  supplier_receipt_create_view, SupplierReceiptListView, supplier_receipt_update_view, supplier_receipt_delete_view, 
supplier_receipt_detail_view, supplier_receipt_show, supplier_receipt_invoice_view)


app_name = 'supplier'

urlpatterns = [
    path('suppliers/', SupplierListView.as_view(), name='supplier_list'),
    path('suppliers/new/', SupplierCreateView.as_view(), name='supplier_create'),
    path('suppliers/<pk>/update/', SupplierUpdateView.as_view(), name='supplier_update'),
    path('suppliers/delete/', supplier_delete_view, name='supplier_delete'),
    path('suppliers/<pk>/details', SupplierDetailView.as_view(), name='supplier_details'),
    path('supplier/invoices/new/', invoice_create_view, name='supplier_invoice_create'),
    path('supplier/invoices/', invoice_list_view, name='supplier_invoice_list'),
    path('supplier/invoices/<pk>/update/', invoice_update_view, name='supplier_invoice_update'),
    path('supplier/invoices/<pk>/show/', invoice_show, name='supplier_invoice_show'),
    path('supplier/invoices/delete/', invoice_delete_view, name='supplier_invoice_delete'),
    path('supplier/invoices/<pk>/', invoice_detail_view, name='supplier_invoice_details'),
    path('supplier/invoices/<pk>/items/', invoice_item_create_view, name='supplier_invoice_item_create'),
    path('supplier/invoices/items/delete/', invoice_item_delete_view, name='supplier_invoice_item_delete'),
    path('supplier/receipts/new/', supplier_receipt_create_view, name='supplier_receipt_create'),
    path('supplier/receipts/', SupplierReceiptListView.as_view(), name='supplier_receipt_list'),
    path('supplier/receipts/<pk>/update/', supplier_receipt_update_view, name='supplier_receipt_update'),
    path('supplier/receipts/delete/', supplier_receipt_delete_view, name='supplier_receipt_delete'),
    path('supplier/receipts/<pk>/items/', supplier_receipt_invoice_view, name='supplier_receipt_invoice'),
    path('supplier/receipts/<pk>/details/', supplier_receipt_detail_view, name='supplier_receipt_details'),
    path('supplier/receipts/<pk>/show/', supplier_receipt_show, name='supplier_receipt_show'),
    
]


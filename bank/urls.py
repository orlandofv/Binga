# -*- coding: utf-8 -*-
from django.conf import settings
from django.conf.urls.static import static

from django.urls import path

from .views import (bank_create_view, bank_list_view, bank_update_view, bank_delete_view, 
bank_detail_view,
bank_account_create_view, bank_account_list_view, bank_account_update_view, bank_account_delete_view, 
bank_account_detail_view)

app_name = 'bank'

urlpatterns = [
path('banks/new/', bank_create_view, name='bank_create'),
path('banks/', bank_list_view, name='bank_list'),
path('banks/<slug:slug>/update/', bank_update_view, name='bank_update'),
path('banks/delete/', bank_delete_view, name='bank_delete'),
path('banks/<slug:slug>/details/', bank_detail_view, name='bank_details'),
path('banks/accounts/new/', bank_account_create_view, name='bank_account_create'),
path('banks/accounts/', bank_account_list_view, name='bank_account_list'),
path('banks/accounts/<slug:slug>/update/', bank_account_update_view, name='bank_account_update'),
path('banks/accounts/delete/', bank_account_delete_view, name='bank_account_delete'),
path('banks/accounts/<slug:slug>/details/', bank_account_detail_view, name='bank_account_details'),
]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)


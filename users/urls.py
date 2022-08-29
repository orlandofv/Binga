# -*- coding: utf-8 -*-
from django.urls import path

from users import views
from django.conf.urls import url

app_name = 'users'
username_regex = r'[a-zA-Z0-9_]+'

handler404 = '{app_name}.views.handler404'.format(app_name=app_name)
handler500 = '{app_name}.views.handler500'.format(app_name=app_name)

urlpatterns = [
    path('users/register/', views.signup, name='register'),
    path('users/login/', views.user_login, name='login'),
    path('users/logout/', views.logout_view, name='logout'),
    path('users/new/', views.user_create_view, name='user_create'),
    path('users/', views.user_list_view, name='user_list'),
    path('users/<pk>/update/', views.user_update_view, name='user_update'),
    path('users/delete/', views.user_delete_view, name='user_delete'),
    path('users/<pk>/', views.user_detail_view, name='user_details'),
]


"""django_project URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('marandzas/', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('marandzas/', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('marandzas/asset_app/', include('blog.urls'))
"""
from django.apps import apps
from django.conf.urls.i18n import i18n_patterns
from django.contrib import admin
from django.contrib.auth import views as auth_views
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static


urlpatterns = i18n_patterns(
    path('marandzas/i18n/', include('django.conf.urls.i18n')),
    path('marandzas/admin/password_reset/', auth_views.PasswordResetView.as_view(), name='admin_password_reset',),
    path('marandzas/admin/password_reset/done/', auth_views.PasswordResetDoneView.as_view(), name='password_reset_done',),
    path('marandzas/reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(), name='password_reset_confirm',),
    path('marandzas/reset/done/', auth_views.PasswordResetCompleteView.as_view(), name='password_reset_complete',),
    # path('marandzas/accounts/', include('django.contrib.auth.urls')), # new
    
    path('marandzas/admin/', admin.site.urls),
    path('marandzas/rosetta/', include('rosetta.urls')),
    path('marandzas/', include('asset_app.urls')),
    path('marandzas/', include('isis.urls')),
    path('marandzas/', include('supplier.urls')),
    path('marandzas/', include('warehouse.urls')),
    path('marandzas/', include('stock.urls')),
    path('marandzas/', include('users.urls')),
    path('marandzas/', include('bank.urls')),
    path('marandzas/', include('costumer.urls')),
    path('marandzas/__debug__/', include('debug_toolbar.urls')),
)

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

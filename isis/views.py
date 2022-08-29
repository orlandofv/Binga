# -*- coding: utf-8 -*-

import datetime
import json
from decimal import Decimal
from math import prod
import sys
import os

from django.utils import timezone
from django.db.models import DecimalField
from django.db.models import Sum, Value as V, F, Q
from django.db.models.functions import Coalesce
from django.db.models.functions import Coalesce
from django.db import connection, IntegrityError
from django.template.defaultfilters import slugify
from django.shortcuts import render, redirect, HttpResponseRedirect, get_object_or_404, HttpResponse
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.views.generic import (
    ListView,
    DetailView,
    CreateView,
    UpdateView,
    DeleteView
)
from django.contrib.auth.models import User
from django.contrib import messages #import messages
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.decorators import login_required
from django.conf import settings
from django.contrib.staticfiles.finders import find
from django.templatetags.static import static
from django.forms import ValidationError

from config import utilities
from asset_app.forms import CostumerForm
from asset_app.models import Costumer
from .models import (Gallery, Product, Tax, Warehouse, Invoice, PaymentTerm, PaymentMethod, Receipt, 
InvoiceItem, Category, ReceiptInvoice, Document, Invoicing, InvoicingItem, DocumentPayment, 
ProductReturn, ProductReturnItem)
from users.models import User
from .forms import (ProductForm, TaxForm, PaymentTermForm, 
PaymentMethodForm, ReceiptForm, CategoryForm, 
DocumentForm, InvoicingForm, InvoicingItemForm, ProductReturnItemForm)

from warehouse.models import Warehouse
from warehouse.forms import WarehouseForm
from asset_app.models import (Costumer, Settings)
from stock.models import Stock
from stock.forms import StockSearchForm
from bank.forms import BankAccountForm
from bank.models import BankAccount

from utilities.utilities import increment_invoice_number, increment_document_number, save_bank_account

PRODUCT_SAVED = False


########################## Category ##########################
class CategoryListView(LoginRequiredMixin, ListView):
    queryset = Category.objects.all()
    template_name = 'isis/listviews/category_list.html'


@login_required
def category_create_view(request):
    if request.method == 'POST':

        form = CategoryForm(request.POST, request.FILES)
        if form.is_valid():
            instance = form.save(commit=False)
            
            parent = request.POST.get('parent')
            
            if parent == "":
                instance.parent = 0
            else:
                instance.parent = parent

            instance.created_by = instance.modified_by = request.user
            instance.date_created = instance.date_modified = datetime.datetime.now()
            instance = instance.save()
            messages.success(request, _("Category added successfully!"))

            if request.POST.get('save_category'):
                return redirect('isis:category_list')
            else:
                return redirect('isis:category_create')
        else:
            print(form.errors)
            for error in form.errors.values():
                messages.error(request, error)
            return redirect('isis:category_create')
    else:
        form = CategoryForm()
        context = {'form': form}
        return render(request, 'isis/createviews/category_create.html', context)


@login_required
def category_update_view(request, slug):
    category = get_object_or_404(Category, slug=slug)
    form = CategoryForm(request.POST or None, request.FILES or None, instance=category)

    if request.method == 'POST':
        
        if form.is_valid():
            print(request.POST)
            
            instance = form.save(commit=False)
            instance.modified_by = request.user
            instance.slug = slugify(instance.name)
            instance.date_modified = datetime.datetime.now()

            parent = request.POST.get('parent')
            if parent == "":
                instance.parent = 0
            else:
                instance.parent = parent

            instance = instance.save()
            messages.success(request, _("Category updated successfully!"))

            if request.POST.get('save_category'):
                return redirect('isis:category_list')
            else:
                return redirect('isis:category_create')

        else:
            print(form.errors)
            for error in form.errors.values():
                messages.error(request, error)
            return redirect('isis:category_update', slug=slug)

    context = {'form': form}
    return render(request, 'isis/updateviews/category_update.html', context)


@login_required
def category_delete_view(request):
    if request.is_ajax():
        selected_ids = request.POST['check_box_item_ids']
        selected_ids = json.loads(selected_ids)
        for i, id in enumerate(selected_ids):
            if id != '':
                try:
                    Category.objects.filter(id__in=selected_ids).delete()
                except Exception as e:
                    messages.warning(request, _("Not Deleted! {}".format(e)))
                    return redirect('isis:category_list')
        
        messages.warning(request, _("Category delete successfully!"))
        return redirect('isis:category_list')


@login_required
def category_detail_view(request, slug):
    # dictionary for initial data with
    # field names as keys
    category = get_object_or_404(Category, slug=slug)

    child_categories = Category.objects.filter(parent=category.id)
    
    try:
        parent_category = Category.objects.get(id=category.parent)
    except Category.DoesNotExist:
        parent_category = _('No parent')

    context ={}
    # add the dictionary during initialization
    context["category"] = category    
    context["child_categories"] = child_categories    
    context["parent_category"] = parent_category

    return render(request, "isis/detailviews/category_detail_view.html", context)


@login_required
def product_list_view(request):
    product = Product.objects.all()
    context = {}
    context['object_list'] = product

    return render(request, 'isis/listviews/product_list.html', context) 

@login_required
def product_create_view(request):
    print('Create product')
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES)
        tax_form = TaxForm(request.POST)
        warehouse_form = WarehouseForm(request.POST)
        category_form = CategoryForm(request.POST)
        
        if request.POST.get('save_tax') or request.POST.get('save_tax_new'):
            if tax_form.is_valid():
                instance = tax_form.save(commit=False)
                instance.created_by = instance.modified_by = request.user
                instance.date_created = instance.date_modified = datetime.datetime.now()
                instance = instance.save()

                return redirect('isis:product_create')
            else:
                for error in tax_form.errors.values():
                    messages.error(request, error)
                return redirect('isis:product_create')

        if request.POST.get('save_warehouse') or request.POST.get('save_warehouse_new'):
            if warehouse_form.is_valid():
                instance = warehouse_form.save(commit=False)
                parent = request.POST.get('parent')
                
                if parent == "":
                    instance.parent = 0
                else:
                    instance.parent = parent
                instance.created_by = instance.modified_by = request.user
                instance.date_created = instance.date_modified = datetime.datetime.now()
                instance = instance.save()

                return redirect('isis:product_create')
            else:
                for error in warehouse_form.errors.values():
                    messages.error(request, error)
                return redirect('isis:product_create')

        if request.POST.get('save_category') or request.POST.get('save_category_new'):
            if category_form.is_valid():
            
                instance = category_form.save(commit=False)
                parent = request.POST.get('parent')
                
                if parent == "":
                    instance.parent = 0
                else:
                    instance.parent = parent

                instance.created_by = instance.modified_by = request.user
                instance.date_created = instance.date_modified = datetime.datetime.now()
                instance = instance.save()

                return redirect('isis:product_create')
            else:
                for error in category_form.errors.values():
                    messages.error(request, error)
                return redirect('isis:product_create')

        if form.is_valid():
            instance = form.save(commit=False)
            instance.created_by = instance.modified_by = request.user
            instance.date_created = instance.date_modified = datetime.datetime.now()
                
            product = instance
            instance = instance.save()
            
            slug = slugify(product.name)
            
            messages.success(request, _("Product added successfully!"))

            if request.POST.get('save_product'):
                return redirect('isis:product_details', slug=slug)
            else:
                return redirect('isis:product_create')
        else:
            print(form.errors)
            for error in form.errors.values():
                messages.error(request, error)
            return redirect('isis:product_create')
    else:
        form = ProductForm()
        tax_form = TaxForm()
        warehouse_form = WarehouseForm()
        category_form = CategoryForm()
        
        context = {'form': form, 'tax_form': tax_form, 
        'warehouse_form': warehouse_form, 'category_form': category_form}

        return render(request, 'isis/createviews/product_create.html', context)


def get_model_name_from_id(model, id):
    try:
        product = model.objects.get(id=id)
        return product.name
    except model.DoesNotExist:
        return None

@login_required
def product_update_view(request, slug):
    product = get_object_or_404(Product, slug=slug)
    form = ProductForm(request.POST or None, request.FILES or None, instance=product)
    tax_form = TaxForm(request.POST or None)
    warehouse_form = WarehouseForm(request.POST or None)
    category_form = CategoryForm(request.POST or None)

    if request.method == 'POST':

        if request.POST.get('save_tax') or request.POST.get('save_tax_new'):
            if tax_form.is_valid():
            
                instance = tax_form.save(commit=False)
                instance.created_by = instance.modified_by = request.user
                instance.date_created = instance.date_modified = datetime.datetime.now()
                instance = instance.save()

                return redirect('isis:product_update', slug=slug)
            else:
                for error in tax_form.errors.values():
                    messages.error(request, error)
                return redirect('isis:product_update', slug=slug)

        if request.POST.get('save_warehouse') or request.POST.get('save_warehouse_new'):
            if warehouse_form.is_valid():
            
                instance = warehouse_form.save(commit=False)
                parent = request.POST.get('parent')
                
                if parent == "":
                    instance.parent = 0
                else:
                    instance.parent = parent
                instance.created_by = instance.modified_by = request.user
                instance.date_created = instance.date_modified = datetime.datetime.now()
                instance = instance.save()

                return redirect('isis:product_update', slug=slug)
            else:
                for error in warehouse_form.errors.values():
                    messages.error(request, error)
                return redirect('isis:product_update', slug=slug)

        if request.POST.get('save_category') or request.POST.get('save_category_new'):
            if category_form.is_valid():
            
                instance = category_form.save(commit=False)
                parent = request.POST.get('parent')
                
                if parent == "":
                    instance.parent = 0
                else:
                    instance.parent = parent
                instance.created_by = instance.modified_by = request.user
                instance.date_created = instance.date_modified = datetime.datetime.now()
                instance = instance.save()

                return redirect('isis:product_update', slug=slug)
            else:
                for error in category_form.errors.values():
                    messages.error(request, error)
                return redirect('isis:product_update', slug=slug)

        if form.is_valid():
            instance = form.save(commit=False)
            instance.modified_by = request.user
            instance.slug = slugify(instance.name)
            instance.date_modified = datetime.datetime.now()

            instance = instance.save()
            messages.success(request, _("Product updated successfully!"))

            if request.POST.get('save_product'):
                return redirect('isis:product_details', slug=slug)
            else:
                return redirect('isis:product_update', slug=slug)

        else:
            for error in form.errors.values():
                messages.error(request, error)
            return redirect('isis:product_update', slug=slug)

    context = {'form': form, 'tax_form': tax_form, 'warehouse_form': warehouse_form,
    'category_form': category_form,}
    return render(request, 'isis/updateviews/product_update.html', context)


@login_required
def product_delete_view(request):
    if request.is_ajax():
        selected_ids = request.POST['check_box_item_ids']
        selected_ids = json.loads(selected_ids)
        for i, id in enumerate(selected_ids):
            if id != '':
                try:
                    Product.objects.filter(id__in=selected_ids).delete()
                    # Set parent to No parent in products with deleted parents
                    Product.objects.filter(parent__in=selected_ids).update(parent=0)
                except Exception as e:
                    messages.warning(request, _("Not Deleted! {}".format(e)))
                    return redirect('isis:product_list')
        
        messages.warning(request, _("Product delete successfully!"))
        return redirect('isis:product_list')


def product_dashboard_view(request):
    ROUTINE = 'Routine'
    PREVENTIVE = 'Preventive'
    CORRECTIVE = 'Corrective'
    PREDECTIVE = 'Predective'

    last_products =  Product.objects.all().order_by('-date_created')[:15]
    total_products =  Product.objects.all().count()
    all_products = Product.objects.all().order_by('name')
    
    context = {}
    context['total'] = total_products
    context['last'] = last_products
    context['all'] = all_products
    
    return render(request, 'isis/dashboardviews/product_dashboard.html', context=context)

def get_product_type(product):
    if product.type == "PRODUCT":
        return 'Product'
    return 'Service'

@login_required
def product_detail_view(request, slug):
    # dictionary for initial data with
    # field names as keys
    product = get_object_or_404(Product, slug=slug)

    product_type = get_product_type(product)
    
    context ={}
    # add the dictionary during initialization
    context["product"] = product     
    context["product_type"] = product_type    

    return render(request, "isis/detailviews/product_detail_view.html", context)


@login_required
def tax_create_view(request):
    if request.method == 'POST':
        form = TaxForm(request.POST)
        
        if form.is_valid():
            instance = form.save(commit=False)
            instance.created_by = instance.modified_by = request.user
            instance.date_created = instance.date_modified = datetime.datetime.now()
            tax = instance
            instance = instance.save()
            
            slug = slugify(tax.name)
            
            messages.success(request, _("Tax added successfully!"))

            if request.POST.get('save_tax'):
                return redirect('isis:tax_list')
            else:
                return redirect('isis:tax_create')
        else:
            for error in form.errors.values():
                messages.error(request, error)
            return redirect('isis:tax_create')
    else:
        form = TaxForm()
        context = {'form': form}
        return render(request, 'isis/createviews/tax_create.html', context)


@login_required
def tax_list_view(request):
    tax = Tax.objects.all()
    context = {}
    context['object_list'] = tax

    return render(request, 'isis/listviews/tax_list.html', context) 


@login_required
def tax_update_view(request, slug):
    tax = get_object_or_404(Tax, slug=slug)
    form = TaxForm(request.POST or None, instance=tax)
	
    if request.method == 'POST':

        if form.is_valid():
            instance = form.save(commit=False)
            instance.modified_by = request.user
            instance.slug = slugify(instance.name)
            instance.date_modified = datetime.datetime.now()
            instance = instance.save()
            messages.success(request, _("Tax updated successfully!"))

            if request.POST.get('save_tax'):
                return redirect('isis:tax_list')
            else:
                return redirect('isis:tax_create')

        else:
            for error in form.errors.values():
                messages.error(request, error)
            return redirect('isis:tax_update', slug=slug)

    context = {'form': form}
    return render(request, 'isis/updateviews/tax_update.html', context)


@login_required
def tax_delete_view(request):
    if request.is_ajax():
        selected_ids = request.POST['check_box_item_ids']
        selected_ids = json.loads(selected_ids)
        for i, id in enumerate(selected_ids):
            if id != '':
                try:
                    Tax.objects.filter(id__in=selected_ids).delete()
                except Exception as e:
                    messages.warning(request, _("Not Deleted! {}".format(e)))
                    return redirect('isis:tax_list')
        
        messages.warning(request, _("Tax delete successfully!"))
        return redirect('isis:tax_list')

@login_required
def tax_detail_view(request, slug):
    # dictionary for initial data with
    # field names as keys
    tax = get_object_or_404(Tax, slug=slug)

    context ={}
    # add the dictionary during initialization
    context["tax"] = tax    
    return render(request, "isis/detailviews/tax_detail_view.html", context)

def get_product_name(id):
    try:
        product = Product.objects.get(id=id)
        return product
    except Product.DoesNotExist:
        return None


def get_product_id(product_name):
    try:
        product = Product.objects.get(name=product_name)
        return product
    except Product.DoesNotExist:
        return None


def get_or_save_product(request, product_id, tax, warehouse):

    # Session that controls if the product was added dynamically or not 
    # Sessions work as global variables
    new_product = request.session.get('new_product')

    print('New product ', new_product)
    print('Product ID', product_id)

    if product_id == "":
        return False
        
    try:
        # Workaround to avoid product duplication error on DB
        if new_product:
            print('Product is new')
            product = Product.objects.filter(name=product_id).first()
            request.session['new_product'] = False
        else:
            print('Product exists')
            product = Product.objects.filter(id=int(product_id)).first()
            print('passei da merda')
    except (Product.DoesNotExist, ValueError) as e:
        print(e)
        product = None
    
    if product is None or product == "":
        print('New product is being saved')
        if request.user.is_staff:
            import random

            user = request.user
            chars = 'ABCDEFGHIJKLMNOPKRSTUVXYZabcdefghijklmnopkqrstuvxwz1234567890'
            code = ''.join(random.choice(chars) for i in range(8))
            type = request.POST.get('type') or 'PRODUCT'
            sell_price = request.POST.get('price') or '0'
            tax_object = Tax.objects.get(rate=tax) or '0'

            category = Category.objects.all().first()

            slug = slugify(product_id)
            product = Product(code=code, name=product_id, slug=slug, tax=tax_object, warehouse=warehouse, 
            created_by=user, category=category, modified_by=request.user, type=type, sell_price=sell_price)
            product.save()

            # Session that controls if the product was added dinamically or not 
            request.session['new_product'] = True

        else:
            messages.error(request, _("Please contact Administrator to add new Products!"))
        
    return product


def get_static(path):
    if settings.DEBUG:
        return find(path)
    else:
        return static(path)

def create_pdf():
    from PyQt5 import QtWidgets, QtWebEngineWidgets
    from PyQt5.QtCore import QUrl
    from PyQt5.QtGui import QPageLayout, QPageSize
    from PyQt5.QtWidgets import QApplication
    from django.templatetags.static import static

    app = QtWidgets.QApplication([])
    loader = QtWebEngineWidgets.QWebEngineView()
    loader.setZoomFactor(1)
    layout = QPageLayout()
    layout.setPageSize(QPageSize(QPageSize.A5))
    layout.setOrientation(QPageLayout.Portrait)
    file = get_static('documents/invoice.html')
    file_path = str(os.path.realpath(file)).replace('\\', '/')
    print(file_path)
    print(settings.STATIC_URL)
    loader.load(QUrl('file:///{}'.format(file_path)))

    loader.page().pdfPrintingFinished.connect(lambda *args: QApplication.exit())

    def emit_pdf(finished):
        loader.page().printToPdf("test.pdf", pageLayout=layout)

    loader.loadFinished.connect(emit_pdf)
    app.exec_()

def manage_stock(request,  document, product, quantity, warehouse, costumer, origin):
    user = request.user
    date = datetime.datetime.now()

    stock = Stock(product=product, document=document, quantity=quantity, warehouse=warehouse,
    costumer=costumer, origin=origin, modified_by=user, created_by=user, date_modified=date, date_created=date)
    
    # Records stock if product type is not service
    if product.is_product:
        stock.save()

    return stock

def load_sell_prices(request):
    product_id = request.GET.get('product')
    
    warehouse = Warehouse.objects.all().first()
    tax = Tax.objects.all().first()

    product_object = get_or_save_product(request, product_id, tax.rate, warehouse)

    try:
        prices = Product.objects.get(id=product_object.id)
        return render(request, 'isis/partials/sell_price_list.html', {'prices': prices})
    except Product.DoesNotExist as e:
        print(e)
    
@login_required
def receipt_show(request, slug):
    """
    Displays Receipt for printing, export, ...
    """
    receipt = get_object_or_404(Receipt, slug=slug)
    items = ReceiptInvoice.objects.filter(receipt=receipt)


    total = items.aggregate(total=Coalesce(Sum('paid'), V(0), output_field=DecimalField()))

    costumer = Costumer.objects.get(id=receipt.costumer.id)
    company = Settings.objects.first()

    context = {'receipt': receipt, 'items': items,  
    'total': total, 'costumer': costumer, 'company': company}

    return render(request, 'isis/documents/receipt.html', context) 

@login_required
def payment_method_create_view(request):
    if request.method == 'POST':
        form = PaymentMethodForm(request.POST)
        
        if form.is_valid():
            instance = form.save(commit=False)
            instance.created_by = instance.modified_by = request.user
            instance.date_created = instance.date_modified = datetime.datetime.now()
            payment_method = instance
            instance = instance.save()

            slug = slugify(payment_method.name)
            messages.success(request, _("PaymentMethod added successfully!"))

            if request.POST.get('save_payment_method'):
                return redirect('isis:payment_method_details', slug=slug)
            else:
                return redirect('isis:payment_method_create')
        else:
            for error in form.errors.values():
                messages.error(request, error)
            return redirect('isis:payment_method_create')
    else:
        form = PaymentMethodForm()
        context = {'form': form}
        return render(request, 'isis/createviews/payment_method_create.html', context)


@login_required
def payment_method_list_view(request):
    payment_method = PaymentMethod.objects.all()
    context = {}
    context['object_list'] = payment_method

    return render(request, 'isis/listviews/payment_method_list.html', context) 


@login_required
def payment_method_update_view(request, slug):
    payment_method = get_object_or_404(PaymentMethod, slug=slug)
    form = PaymentMethodForm(request.POST or None, instance=payment_method)
	
    if request.method == 'POST':

        if form.is_valid():
            instance = form.save(commit=False)
            instance.modified_by = request.user
            instance.slug = slugify(instance.name)
            instance.date_modified = datetime.datetime.now()
            instance = instance.save()
            messages.success(request, _("PaymentMethod updated successfully!"))

            if request.POST.get('save_payment_method'):
                return redirect('isis:payment_method_list')
            else:
                return redirect('isis:payment_method_create')

        else:
            for error in form.errors.values():
                messages.error(request, error)
            return redirect('isis:payment_method_update', slug=slug)

    context = {'form': form}
    return render(request, 'isis/updateviews/payment_method_update.html', context)


@login_required
def payment_method_delete_view(request):
    if request.is_ajax():
        selected_ids = request.POST['check_box_item_ids']
        selected_ids = json.loads(selected_ids)
        for i, id in enumerate(selected_ids):
            if id != '':
                try:
                    PaymentMethod.objects.filter(id__in=selected_ids).delete()
                except Exception as e:
                    messages.warning(request, _("Not Deleted! {}".format(e)))
                    return redirect('isis:payment_method_list')
        
        messages.warning(request, _("PaymentMethod delete successfully!"))
        return redirect('isis:payment_method_list')


@login_required
def payment_term_create_view(request):
    if request.method == 'POST':
        form = PaymentTermForm(request.POST)
        
        if form.is_valid():
            instance = form.save(commit=False)
            instance.created_by = instance.modified_by = request.user
            instance.date_created = instance.date_modified = datetime.datetime.now()
            payment_term = instance
            instance = instance.save()

            slug = slugify(payment_term.name)
            messages.success(request, _("PaymentTerm added successfully!"))

            if request.POST.get('save_payment_term'):
                return redirect('isis:payment_term_details', slug=slug)
            else:
                return redirect('isis:payment_term_create')
        else:
            for error in form.errors.values():
                messages.error(request, error)
            return redirect('isis:payment_term_create')
    else:
        form = PaymentTermForm()
        context = {'form': form}
        return render(request, 'isis/createviews/payment_term_create.html', context)


@login_required
def payment_term_list_view(request):
    payment_term = PaymentTerm.objects.all()
    context = {}
    context['object_list'] = payment_term

    return render(request, 'isis/listviews/payment_term_list.html', context) 


@login_required
def payment_term_update_view(request, slug):
    payment_term = get_object_or_404(PaymentTerm, slug=slug)
    form = PaymentTermForm(request.POST or None, instance=payment_term)
	
    if request.method == 'POST':

        if form.is_valid():
            instance = form.save(commit=False)
            instance.modified_by = request.user
            instance.slug = slugify(instance.name)
            instance.date_modified = datetime.datetime.now()
            instance = instance.save()
            messages.success(request, _("PaymentTerm updated successfully!"))

            if request.POST.get('save_payment_term'):
                return redirect('isis:payment_term_list')
            else:
                return redirect('isis:payment_term_create')

        else:
            for error in form.errors.values():
                messages.error(request, error)
            return redirect('isis:payment_term_update', slug=slug)

    context = {'form': form}
    return render(request, 'isis/updateviews/payment_term_update.html', context)


@login_required
def payment_term_delete_view(request):
    if request.is_ajax():
        selected_ids = request.POST['check_box_item_ids']
        selected_ids = json.loads(selected_ids)
        for i, id in enumerate(selected_ids):
            if id != '':
                try:
                    PaymentTerm.objects.filter(id__in=selected_ids).delete()
                except Exception as e:
                    messages.warning(request, _("Not Deleted! {}".format(e)))
                    return redirect('isis:payment_term_list')
        
        messages.warning(request, _("PaymentTerm delete successfully!"))
        return redirect('isis:payment_term_list')


class ReceiptListView(LoginRequiredMixin, ListView):
    initial_date = timezone.now()
    final_date = timezone.now()

    form_class = StockSearchForm

    queryset = Receipt.objects.filter(date_created__gte=initial_date,
    date_created__lte=final_date)

    template_name = 'isis/listviews/receipt_list.html'

    def post(self, request, *args, **kwargs):
        form_class = self.get_form_class()
        form = self.get_form(form_class)

        initial_date = self.request.POST.get('initial_date')
        final_date = self.request.POST.get('final_date')

        if form.is_valid():
            self.queryset = Receipt.objects.filter(date_created__gte=initial_date,
            date_created__lte=final_date)
        else:
            for error in form.errors.values():
                messages.error(request, error)
            return self.form_invalid(form)

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        context['object_list'] = self.queryset
        form_class = self.get_form_class()
        form = self.get_form(form_class)
        context['search_form'] = form

        return context


def make_payment(receipt, invoice, debit, credit, total, payment):
    
    # Total payment is equal or superior to debt
    if Decimal(payment) + Decimal(credit) >= Decimal(total):
        payment = Decimal(total) - Decimal(credit)
        inv = Invoice.objects.filter(id=invoice.id).update(
            credit=Decimal(total),
            debit=0,
            paid_status=1
            )
    else:
        inv = Invoice.objects.filter(id=invoice.id).update(
            credit=F('credit') + Decimal(payment),
            debit=F('debit') - Decimal(payment)
        )

    r = ReceiptInvoice(receipt=receipt, invoice=invoice, debit=Decimal(debit),
    paid=Decimal(payment), remaining=invoice.debit-Decimal(payment))
    r.save()

    return inv


@login_required
def receipt_invoice_view(request, slug):
    receipt = get_object_or_404(Receipt, slug=slug)

    if receipt.is_finished():
        messages.warning(request,_('Receipt is closed and cannot be edited.'))
        return redirect('isis:receipt_list')

    invoices = Invoice.objects.filter(costumer=receipt.costumer,
    paid_status=0, active_status=1, finished_status=1).order_by('date_created')

    if not invoices:
        messages.warning(request, _("This costumer has no pending invoices!"))
        return redirect('isis:receipt_list')

    if request.method == 'POST':
        # convert django query dict to python dictionary
        data = dict(request.POST)
        invoices = data['invoices']
        t = 0
        for inv in invoices:
            credit = data['invoice_credit'][t]
            total = data['invoice_total'][t]
            payment = data['payment'][t]
            debit = data['invoice_debit'][t]

            invoice = Invoice.objects.get(id=int(inv))

            make_payment(receipt, invoice, debit, credit, total, payment)
            t += 1

        Receipt.objects.filter(id=receipt.id).update(finished_status=1)
        return redirect('isis:receipt_show', slug=slug)

    context = {'receipt': receipt, 'invoices': invoices}
    return render(request, 'isis/createviews/receipt_invoice.html', context=context)


def check_costumer_invoices(costumer):
    '''
    # Checks weather costumer has pending Invoices or not
    '''
    invoices = Invoice.objects.filter(costumer_id=int(costumer),
    paid_status=0, active_status=1, finished_status=1).order_by('date_created')

    if not invoices:
        return False
    
    return True

@login_required
def receipt_create_view(request):
    
    if request.method == 'POST':
        costumer = request.POST.get('costumer')
        if not costumer:
            messages.warning(request, _("There are no invoices with pending payments! Please create Invoice First."))
            return redirect('isis:invoice_create')
        
        costumer_invoices = check_costumer_invoices(costumer)

        # Checks weather costumer has pending Invoices or not
        if not costumer_invoices:
            messages.warning(request, _("This costumer has no pending invoices!"))
            return redirect('isis:receipt_list')

        form = ReceiptForm(request.POST)
        if form.is_valid():
            instance = form.save(commit=False)
            instance.created_by = instance.modified_by = request.user
            instance.date_created = instance.date_modified = datetime.datetime.now()
            instance.credit = 0
            instance.debit = 0

            document_number = increment_invoice_number(Receipt)

            instance.number = document_number
            name = '{} {}'.format(_('Receipt'), document_number)
        
            instance.name = name
            slug = slugify(name)
            instance.slug = slugify(name)
            instance = instance.save()
    
            return redirect('isis:receipt_invoice', slug=slug)
            
        else:
            print(form.errors)
            for error in form.errors.values():
                messages.error(request, error)
            return redirect('isis:receipt_create')
    else:
        form = ReceiptForm()
        context = {'form': form}
        return render(request, 'isis/createviews/receipt_create.html', context)


@login_required
def receipt_update_view(request, slug):
    receipt = get_object_or_404(Receipt, slug=slug)
    form = ReceiptForm(request.POST or None, instance=receipt)

    if request.method == 'POST':
        if form.is_valid():
            instance = form.save(commit=False)
            instance.modified_by = request.user
            instance.slug = slugify(instance.name)
            instance.date_modified = datetime.datetime.now()
            instance = instance.save()
            
            if request.POST.get('save_receipt'):
                return redirect('isis:receipt_list')
            else:
                return redirect('isis:receipt_create')

        else:
            for error in form.errors.values():
                messages.error(request, error)
            return redirect('isis:receipt_update', slug=slug)

    context = {'form': form}
    return render(request, 'isis/updateviews/receipt_update.html', context)


@login_required
def receipt_delete_view(request):
    if request.is_ajax():
        selected_ids = request.POST['check_box_item_ids']
        selected_ids = json.loads(selected_ids)
        for i, id in enumerate(selected_ids):
            if id != '':
                try:
                    Receipt.objects.filter(id__in=selected_ids).delete()
                except Exception as e:
                    messages.warning(request, _("Not Deleted! {}".format(e)))
                    return redirect('isis:receipt_list')
        
        messages.warning(request, _("Receipt delete successfully!"))
        return redirect('isis:receipt_list')


@login_required
def receipt_detail_view(request, slug):
    receipt = get_object_or_404(Receipt, slug=slug)
    invoice_items = ReceiptInvoice.objects.filter(receipt=receipt)

    # Field totals
    total = invoice_items.aggregate(total=Coalesce(Sum('debit'), V(0), output_field=DecimalField()))
    total_paid = invoice_items.aggregate(total=Coalesce(Sum('paid'), V(0), output_field=DecimalField()))
    total_debt = invoice_items.aggregate(total=Coalesce(Sum('remaining'), V(0), output_field=DecimalField()))

    context ={}
    # add the dictionary during initialization
    context["receipt"] = receipt    
    context["invoices"] = invoice_items
    context["total"] = total
    context["total_paid"] = total_paid
    context["total_debt"] = total_debt

    return render(request, "isis/detailviews/receipt_detail_view.html", context)


########################## Document ##########################
class DocumentListView(LoginRequiredMixin, ListView):
    model = Document
    template_name = 'isis/listviews/document_list.html'


@login_required
def document_create_view(request):
    if request.method == 'POST':
        form = DocumentForm(request.POST)

        if form.is_valid():
            instance = form.save(commit=False)
            instance.created_by = instance.modified_by = request.user
            instance.date_created = instance.date_modified = datetime.datetime.now()
            instance = instance.save()
            messages.success(request, _("Document added successfully!"))

            if request.POST.get('save_document'):
                return redirect('isis:document_list')
            else:
                return redirect('isis:document_create')
        else:
            for error in form.errors.values():
                messages.error(request, error)
            return redirect('isis:document_create')
    else:
        form = DocumentForm()
        context = {'form': form}
        return render(request, 'isis/createviews/document_create.html', context)


@login_required
def document_update_view(request, slug):
    document = get_object_or_404(Document, slug=slug)
    form = DocumentForm(request.POST or None, instance=document)

    if request.method == 'POST':
        
        if form.is_valid():
            instance = form.save(commit=False)
            instance.modified_by = request.user
            instance.slug = slugify(instance.name)
            instance.date_modified = datetime.datetime.now()
            instance = instance.save()
            messages.success(request, _("Document updated successfully!"))

            if request.POST.get('save_document'):
                return redirect('isis:document_list')
            else:
                return redirect('isis:document_create')

        else:
            for error in form.errors.values():
                messages.error(request, error)
            return redirect('isis:document_update', slug=slug)

    context = {'form': form}
    return render(request, 'isis/updateviews/document_update.html', context)


@login_required
def document_delete_view(request):
    if request.is_ajax():
        selected_ids = request.POST['check_box_item_ids']
        selected_ids = json.loads(selected_ids)
        for i, id in enumerate(selected_ids):
            if id != '':
                try:
                    Document.objects.filter(id__in=selected_ids).delete()
                except Exception as e:
                    messages.warning(request, _("Not Deleted! {}".format(e)))
                    return redirect('isis:document_list')
        
        messages.warning(request, _("Document delete successfully!"))
        return redirect('isis:document_list')


@login_required
def document_detail_view(request, slug):
    # dictionary for initial data with
    # field names as keys
    document = get_object_or_404(Document, slug=slug)

    context ={}
    # add the dictionary during initialization
    context["document"] = document    
    return render(request, "isis/detailviews/document_detail_view.html", context)


@login_required
def invoicing_list_view(request):

    start_date = datetime.datetime.now() - datetime.timedelta(days=30)
    end_date = datetime.datetime.now() + datetime.timedelta(days=1)

    if request.method == "POST":
        search_form = StockSearchForm(request.POST)
        start_date = request.POST.get("start_date".replace('T', " "))
        end_date = request.POST.get("end_date")

        invoicing = Invoicing.objects.raw("""
        SELECT inv.*, SUM(item.discount_total) AS ds, SUM(item.sub_total) AS sb, 
        SUM(item.tax_total) AS tax, SUM(item.total) AS tt 
        FROM isis_invoicing AS inv
        LEFT JOIN isis_invoicingitem item ON inv.id=item.invoicing_id
        WHERE inv.date_created BETWEEN '{}' AND '{}'
        GROUP BY inv.id  
        """.format(str(start_date).replace('T', " "), str(end_date).replace('T', " ")))
    else:
        search_form = StockSearchForm()
        invoicing = Invoicing.objects.raw("""
        SELECT inv.*, SUM(item.discount_total) AS ds, SUM(item.sub_total) AS sb, 
        SUM(item.tax_total) AS tax, SUM(item.total) AS tt 
        FROM isis_invoicing AS inv
        LEFT JOIN isis_invoicingitem item ON inv.id=item.invoicing_id
        WHERE inv.date_created BETWEEN '{}' AND '{}'
        GROUP BY inv.id  """.format(start_date, end_date))
    
    context = {}
    context['search_form'] = search_form
    context['object_list'] = invoicing

    return render(request, 'isis/listviews/invoicing_list.html', context) 


@login_required
def invoicing_create_view(request):
    if request.method == 'POST':
        form = InvoicingForm(request.POST)
        costumer_form = CostumerForm(request.POST)
        warehouse_form = WarehouseForm(request.POST)
        payment_term_form = PaymentTermForm(request.POST)
        payment_method_form = PaymentMethodForm(request.POST)
        document_form = DocumentForm(request.POST)
        bank_account_form = BankAccountForm(request.POST)

        if request.POST.get('save_bank_account_new') or request.POST.get('save_bank_account'):
            if bank_account_form.is_valid():
                instance = bank_account_form.save(commit=False)
                instance.created_by = instance.modified_by = request.user
                instance.date_created = instance.date_modified = datetime.datetime.now()
                instance = instance.save()
                return redirect('isis:invoicing_create')
            else:
                for error in costumer_form.errors.values():
                    messages.error(request, error)
                return redirect('isis:invoicing_create')

        if request.POST.get('save_costumer') is not None \
            or request.POST.get('save_costumer_new') is not None:

            if costumer_form.is_valid():
                instance = costumer_form.save(commit=False)
                instance.created_by = instance.modified_by = request.user
                instance.date_created = instance.date_modified = datetime.datetime.now()
                instance.is_costumer = 1
                if request.POST.get('parent') is None or request.POST.get('parent') == "":
                    instance.parent = 0
                else:
                    instance.parent = int(request.POST.get('parent'))
                instance = instance.save()

                return redirect('isis:invoicing_create')
            else:
                for error in costumer_form.errors.values():
                    messages.error(request, error)
                return redirect('isis:invoicing_create')

        if request.POST.get('save_warehouse') or request.POST.get('save_warehouse_new'):
            if warehouse_form.is_valid():
                    instance = warehouse_form.save(commit=False)
                    instance.created_by = instance.modified_by = request.user
                    instance.date_created = instance.date_modified = datetime.datetime.now()
                    if request.POST.get('parent') is None or request.POST.get('parent') == "":
                        instance.parent = 0
                    else:
                        instance.parent = int(request.POST.get('parent'))
                    instance = instance.save()

                    return redirect('isis:invoicing_create')
            else:
                for error in warehouse_form.errors.values():
                    messages.error(request, error)
                return redirect('isis:invoicing_create')

        if request.POST.get('save_payment_method') \
            or request.POST.get('save_payment_method_new'):
            if  payment_method_form.is_valid():
            
                    instance = payment_method_form.save(commit=False)
                    instance.created_by = instance.modified_by = request.user
                    instance.date_created = instance.date_modified = datetime.datetime.now()
                    instance = instance.save()

                    return redirect('isis:invoicing_create')
            else:
                for error in payment_method_form.errors.values():
                    messages.error(request, error)
                return redirect('isis:invoicing_create')

        if request.POST.get('save_payment_term') or \
            request.POST.get('save_payment_term_new'):
            if payment_term_form.is_valid():
                instance = payment_term_form.save(commit=False)
                instance.created_by = instance.modified_by = request.user
                instance.date_created = instance.date_modified = datetime.datetime.now()
                instance = instance.save()

                return redirect('isis:invoicing_create')
            else:
                for error in payment_term_form.errors.values():
                    messages.error(request, error)
                return redirect('isis:invoicing_create')
        
        if request.POST.get('save_document') or request.POST.get('save_document_new'):
            if document_form.is_valid():
                instance = document_form.save(commit=False)
                instance.created_by = instance.modified_by = request.user
                instance.date_created = instance.date_modified = datetime.datetime.now()
                instance = instance.save()

                return redirect('isis:invoicing_create')
            else:
                for error in document_form.errors.values():
                    messages.error(request, error)
                return redirect('isis:invoicing_create')
                
        if form.is_valid():

            instance = form.save(commit=False)
            instance.created_by = instance.modified_by = request.user
            instance.date_created = instance.date_modified = datetime.datetime.now()

            doc = request.POST.get('document')

            document_number = increment_document_number(Invoicing, doc)

            instance.number = document_number
            invoicing = instance
            instance = instance.save()

            return redirect('isis:invoicing_item_create', pk=invoicing.pk)

        else:
            for error in form.errors.values():
                messages.error(request, error)
            return redirect('isis:invoicing_create')
    else:
        form = InvoicingForm()
        costumer_form = CostumerForm()
        warehouse_form = WarehouseForm()
        payment_term_form = PaymentTermForm()
        payment_method_form = PaymentMethodForm()
        document_form = DocumentForm()
        bank_account_form = BankAccountForm()

        context = {'form': form, 'costumer_form': costumer_form, 
        'warehouse_form': warehouse_form, 'payment_term_form': payment_term_form,
        'payment_method_form': payment_method_form, 'document_form': document_form,
        'bank_account_form': bank_account_form}
        return render(request, 'isis/createviews/invoicing_create.html', context)


@login_required
def invoicing_update_view(request, pk):
    invoicing = get_object_or_404(Invoicing, pk=pk)
    
    if invoicing.is_finished():
        messages.warning(request,_('Document is closed and cannot be edited.'))
        return redirect('isis:invoicing_list')

    form = InvoicingForm(request.POST or None, instance=invoicing)
    # Disable document select input
    form.fields['document'].disabled = True 

    costumer_form = CostumerForm(request.POST or None)
    warehouse_form = WarehouseForm(request.POST or None)
    payment_term_form = PaymentTermForm(request.POST or None)
    payment_method_form = PaymentMethodForm(request.POST or None)
    document_form = DocumentForm(request.POST or None)
    bank_account_form = BankAccountForm(request.POST or None)

    if request.method == 'POST':

        if request.POST.get('save_bank_account_new') or request.POST.get('save_bank_account'):
            if bank_account_form.is_valid():
                instance = bank_account_form.save(commit=False)
                instance.created_by = instance.modified_by = request.user
                instance.date_created = instance.date_modified = datetime.datetime.now()
                instance = instance.save()
                return redirect('isis:invoicing_create')
            else:
                for error in costumer_form.errors.values():
                    messages.error(request, error)
                return redirect('isis:invoicing_create')

        if request.POST.get('save_costumer') is not None \
            or request.POST.get('save_costumer_new') is not None:
    
            if costumer_form.is_valid():
                instance = costumer_form.save(commit=False)
                instance.created_by = instance.modified_by = request.user
                instance.date_created = instance.date_modified = datetime.datetime.now()
                instance.is_costumer = 1
                if request.POST.get('parent') is None or request.POST.get('parent') == "":
                    instance.parent = 0
                else:
                    instance.parent = int(request.POST.get('parent'))
                instance = instance.save()

                return redirect('isis:invoicing_update', pk=pk)
            else:
                for error in costumer_form.errors.values():
                    messages.error(request, error)
                return redirect('isis:invoicing_update', pk=pk)

        if request.POST.get('save_warehouse') or request.POST.get('save_warehouse_new'):
            if warehouse_form.is_valid():
                instance = warehouse_form.save(commit=False)
                instance.created_by = instance.modified_by = request.user
                instance.date_created = instance.date_modified = datetime.datetime.now()
                if request.POST.get('parent') is None or request.POST.get('parent') == "":
                    instance.parent = 0
                else:
                    instance.parent = int(request.POST.get('parent'))
                instance = instance.save()

                return redirect('isis:invoicing_update', pk=pk)
            else:
                for error in warehouse_form.errors.values():
                    messages.error(request, error)
                return redirect('isis:invoicing_update', pk=pk)

        if request.POST.get('save_payment_method') \
            or request.POST.get('save_payment_method_new'):
            if  payment_method_form.is_valid():
        
                instance = payment_method_form.save(commit=False)
                instance.created_by = instance.modified_by = request.user
                instance.date_created = instance.date_modified = datetime.datetime.now()
                instance = instance.save()

                return redirect('isis:invoicing_update', pk=pk)
            else:
                for error in payment_method_form.errors.values():
                    messages.error(request, error)
                return redirect('isis:invoicing_update', pk=pk)

        if request.POST.get('save_payment_term') or \
            request.POST.get('save_payment_term_new'):
            if payment_term_form.is_valid():
                instance = payment_term_form.save(commit=False)
                instance.created_by = instance.modified_by = request.user
                instance.date_created = instance.date_modified = datetime.datetime.now()
                instance = instance.save()

                return redirect('isis:invoicing_update', pk=pk)
            else:
                for error in payment_term_form.errors.values():
                    messages.error(request, error)
                return redirect('isis:invoicing_update', pk=pk)
        
        if request.POST.get('save_document') or request.POST.get('save_document_new'):
            if document_form.is_valid():
                instance = document_form.save(commit=False)
                instance.created_by = instance.modified_by = request.user
                instance.date_created = instance.date_modified = datetime.datetime.now()
                instance = instance.save()

                return redirect('isis:invoicing_update', pk=pk)
            else:
                for error in document_form.errors.values():
                    messages.error(request, error)
                return redirect('isis:invoicing_update', pk=pk)
                
        if form.is_valid():

            instance = form.save(commit=False)
            instance.modified_by = request.user
            instance.date_modified = datetime.datetime.now()
            instance = instance.save()

            return redirect('isis:invoicing_item_create', pk=pk)
        else:
            for error in form.errors.values():
                messages.error(request, error)
            return redirect('isis:invoicing_update', pk=pk)

    context = {'form': form, 'costumer_form': costumer_form, 
        'warehouse_form': warehouse_form, 'payment_term_form': payment_term_form,
        'payment_method_form': payment_method_form, 'document_form': document_form,
        'bank_account_form': bank_account_form}
    return render(request, 'isis/createviews/invoicing_create.html', context)


@login_required
def invoicing_delete_view(request):
    if request.is_ajax():
        selected_ids = request.POST['check_box_item_ids']
        selected_ids = json.loads(selected_ids)
        for i, id in enumerate(selected_ids):
            if id != '':
                try:
                    Invoicing.objects.filter(id__in=selected_ids).delete()
                    # Set parent to No parent in invoicing with deleted parents
                    Invoicing.objects.filter(parent__in=selected_ids).update(parent=0)
                except Exception as e:
                    messages.warning(request, _("Not Deleted! {}".format(e)))
                    return redirect('isis:invoicing_list')
        
        messages.warning(request, _("Invoicing delete successfully!"))
        return redirect('isis:invoicing_list')


def invoicing_dashboard_view(request):
    ROUTINE = 'Routine'
    PREVENTIVE = 'Preventive'
    CORRECTIVE = 'Corrective'
    PREDECTIVE = 'Predective'

    last_invoicings =  Invoicing.objects.all().order_by('-date_created')[:15]
    total_invoicings =  Invoicing.objects.all().count()
    all_invoicings = Invoicing.objects.all().order_by('name')
    
    context = {}
    context['total'] = total_invoicings
    context['last'] = last_invoicings
    context['all'] = all_invoicings
    
    return render(request, 'isis/dashboardviews/invoicing_dashboard.html', context=context)

@login_required
def invoicing_detail_view(request, pk):
    # dictionary for initial data with
    # field names as keys
    invoicing = get_object_or_404(Invoicing, pk=pk)
    payments = DocumentPayment.objects.filter(invoicing=invoicing)
    total = payments.aggregate(total=Coalesce(Sum('amount'), V(0), output_field=DecimalField()))
    
    paid_invoicings = Invoicing.objects.filter(costumer=invoicing.costumer, 
    paid_status=1).exclude(id=invoicing.id).order_by('-number')[:5]
    
    overdue_invoicings = Invoicing.objects.filter(costumer=invoicing.costumer, 
    paid_status=0, due_date__lt=datetime.datetime.now()).exclude(id=invoicing.id).order_by('number')
    
    not_paid_invoicings = Invoicing.objects.filter(costumer=invoicing.costumer, 
    paid_status=0).exclude(id=invoicing.id).order_by('number')
    
    context ={}
    # add the dictionary during initialization
    context["invoicing"] = invoicing    
    context["paid_invoicings"] = paid_invoicings     
    context["not_paid_invoicings"] = not_paid_invoicings     
    context["overdue_invoicings"] = overdue_invoicings     
    context["payments"] = payments
    context["total"] = total
    
    return render(request, "isis/detailviews/invoicing_detail_view.html", context)


@login_required
def invoicing_item_delete_view(request):
    
    if request.is_ajax():
        selected_ids = request.POST['check_box_item_ids']
        selected_ids = json.loads(selected_ids)
        
        print(selected_ids)
        if len(selected_ids) == 1 and selected_ids[0] == 'None':
            return redirect('isis:invoicing_item_create')

        if len(selected_ids) > 1:
            item = InvoicingItem.objects.filter(id=int(selected_ids[1])).first()
        else:
            item = InvoicingItem.objects.filter(id=int(selected_ids[0])).first()

        try:
            InvoicingItem.objects.filter(id__in=selected_ids).delete()
            increase_decrease_invoicing_totals(item.invoicing_id)
        except Exception as e:
            messages.warning(request, _("Not Deleted! {}.".format(e)))
            print(e)
            return redirect('isis:invoicing_create')
        return redirect('isis:invoicing_create')


@login_required
def invoicing_item_create_view(request, pk):
    """
    Creates or Adds Invoicing Items
    """
    invoicing = get_object_or_404(Invoicing, pk=pk)
    
    if invoicing.is_finished():
        messages.warning(request,_('Document is closed and cannot be edited.'))
        return redirect('isis:invoicing_list')

    items = InvoicingItem.objects.filter(invoicing=invoicing)

    tax_total = items.aggregate(tax=Coalesce(Sum('tax_total'), V(0), output_field=DecimalField()))
    discount_total = items.aggregate(discount=Coalesce(Sum('discount_total'), V(0), output_field=DecimalField()))
    sub_total = items.aggregate(subtotal=Coalesce(Sum('sub_total'), V(0), output_field=DecimalField()))
    total = items.aggregate(total=Coalesce(Sum('total'), V(0), output_field=DecimalField()))

    if request.method == 'POST':
        form = InvoicingItemForm(request.POST)

        if request.POST.get('validate'):
            document = '{} - {}'.format(_('Invoicing'), invoicing.id)

            # Prevent Finishing Empty Invoice 
            if not items:
                messages.warning(request, _("Please create Invoice Items First"))
                return redirect('isis:invoicing_item_create', pk=pk)

            # Records stock movement 
            if invoicing.finished_status == 0:
                for i in items:
                    manage_stock(request, document, i.product, -i.quantity, invoicing.warehouse, invoicing.costumer, 
                "Costumer Invoicing")
        
            if invoicing.document.track_payment == 1:
                return redirect('isis:document_payment', pk=pk)
            else:
                # Changes the Invoicing status to finished_status
                inv = Invoicing.objects.filter(id=invoicing.id).update(finished_status=1)
                return redirect('isis:invoicing_show', pk=pk)         
        else:
            # Records a line to Invoicing
            warehouse = invoicing.warehouse

            if request.POST.get('barcode') != '':
                product = Product.objects.filter(Q(code=str(request.POST.get('barcode'))) |
                Q(barcode=str(request.POST.get('barcode')))).first()

                if product:
                    name = product.id
                    quantity = Decimal(1)
                    tax = product.tax.id
                    discount = Decimal(0)
                    price = product.sell_price
                    product_object = get_or_save_product(request, name, tax, warehouse)
                else:
                    messages.warning(request, _("No product matches the given barcode. Please choose product from the dropdown below."))
                    return redirect('isis:invoicing_item_create', pk=pk)
            else:
                try:
                    name = request.POST.get('product')
                    quantity = Decimal(request.POST.get('quantity'))
                    tax = Decimal(request.POST.get('tax'))
                    discount = Decimal(request.POST.get('discount'))
                    price = Decimal(request.POST.get('price'))

                    product_object = get_or_save_product(request, name, tax, warehouse)
                    
                except Exception as e:
                    messages.warning(request, _("Please use numbers that do not contain commas (','), and use dot ('.') for decimals.\n{}.".format(e)))
                    return redirect('isis:invoicing_item_create', pk=pk)
    
            if not product_object:
                messages.warning(request, _("Please choose product from the dropdown, or add a new product."))
                return redirect('isis:invoicing_item_create', pk=pk)

            if product_object.is_inactive:
                messages.warning(request, _("This product is inactive and cannot be sold.".format(e)))
                return redirect('isis:invoicing_item_create', pk=pk)
            
            if product_object.is_not_for_sale:
                messages.warning(request, _("This product is not for sale.".format(e)))
                return redirect('isis:invoicing_item_create', pk=pk)

            # save the data and after fetch the object in instance
            tax = Tax.objects.filter(id=int(tax)).first()
            instance = InvoicingItem(invoicing=invoicing, tax=tax.rate, quantity=quantity,
            discount= discount, price=price, product=product_object) 
            instance.save()
            
            increase_decrease_invoicing_totals(invoicing.id)

        return redirect('isis:invoicing_item_create', pk=pk)
    else:
        form = InvoicingItemForm(None)
        return render(request, 'isis/createviews/invoicing_item_create.html', 
        {'invoicing': invoicing, 'form': form, 'items': items, 'tax_total': tax_total, 
        'discount_total': discount_total, 'sub_total': sub_total, 'total': total})


@login_required
def invoicing_show(request, pk):
    """
    Displays Invoicing for printing, export, ...
    """
    invoicing = get_object_or_404(Invoicing, pk=pk)
    items = InvoicingItem.objects.filter(invoicing=invoicing)

    if request.method == 'POST':
        create_pdf
    tax_total = items.aggregate(Sum('tax_total'))
    discount_total = items.aggregate(Sum('discount_total'))
    sub_total = items.aggregate(Sum('sub_total'))
    total = items.aggregate(Sum('total'))

    costumer = Costumer.objects.get(id=invoicing.costumer.id)
    company = Settings.objects.first()

    context = {'invoicing': invoicing, 'items': items, 'tax_total': tax_total, 
    'discount_total': discount_total, 'sub_total': sub_total, 
    'total': total, 'costumer': costumer, 'company': company}

    instance = Invoicing.objects.filter(id=invoicing.id).update(finished_status=1)
    return render(request, 'isis/documents/invoicing.html', context) 


@login_required
def invoicing_show_pos(request, pk):
    """
    Displays Invoicing for printing, export, ...
    """
    invoicing = get_object_or_404(Invoicing, pk=pk)
    items = InvoicingItem.objects.filter(invoicing=invoicing)

    if request.method == 'POST':
        create_pdf
    tax_total = items.aggregate(Sum('tax_total'))
    discount_total = items.aggregate(Sum('discount_total'))
    sub_total = items.aggregate(Sum('sub_total'))
    total = items.aggregate(Sum('total'))

    costumer = Costumer.objects.get(id=invoicing.costumer.id)
    company = Settings.objects.first()

    context = {'invoicing': invoicing, 'items': items, 'tax_total': tax_total, 
    'discount_total': discount_total, 'sub_total': sub_total, 
    'total': total, 'costumer': costumer, 'company': company}

    instance = Invoicing.objects.filter(id=invoicing.id).update(finished_status=1)
    return render(request, 'isis/documents/pos_receipt.html', context) 


def increase_decrease_invoicing_totals(invoicing_id):
    """
    Modifies (Decreases or increases) Invoicing totals when item is deleted
    """

    items = InvoicingItem.objects.filter(invoicing=invoicing_id)

    tax_total = items.aggregate(tax=Coalesce(Sum('tax_total'), V(0), output_field=DecimalField()))
    discount_total = items.aggregate(discount=Coalesce(Sum('discount_total'), V(0), output_field=DecimalField()))
    sub_total = items.aggregate(subtotal=Coalesce(Sum('sub_total'), V(0), output_field=DecimalField()))
    total = items.aggregate(total=Coalesce(Sum('total'), V(0), output_field=DecimalField()))

    inv = Invoicing.objects.filter(id=invoicing_id).update(
    debit=total['total'],
    total=total['total'],
    subtotal=sub_total['subtotal'],
    total_tax=tax_total['tax'],
    total_discount=discount_total['discount']
    )

    return inv


def increase_decrease_product_return_totals(invoicing_id):
    """
    Modifies (Decreases or increases) Invoicing totals when item is deleted
    """

    items = ProductReturnItem.objects.filter(product_return=invoicing_id)

    tax_total = items.aggregate(tax=Coalesce(Sum('tax_total'), V(0), output_field=DecimalField()))
    discount_total = items.aggregate(discount=Coalesce(Sum('discount_total'), V(0), output_field=DecimalField()))
    sub_total = items.aggregate(subtotal=Coalesce(Sum('sub_total'), V(0), output_field=DecimalField()))
    total = items.aggregate(total=Coalesce(Sum('total'), V(0), output_field=DecimalField()))

    inv = ProductReturn.objects.filter(id=invoicing_id).update(
    debit=total['total'],
    total=total['total'],
    subtotal=sub_total['subtotal'],
    total_tax=tax_total['tax'],
    total_discount=discount_total['discount']
    )

    return inv

def save_payment_history(amount, notes, file, invoicing, payment_method):
    pm = PaymentMethod.objects.filter(id=payment_method).first()

    if Decimal(amount) > Decimal(0):
        DocumentPayment.objects.create(amount=amount, notes=notes, file=file, 
        invoicing=invoicing, payment_method=pm)


@login_required
def document_payment_view(request, pk):
    invoicing = get_object_or_404(Invoicing, pk=pk)
    payment_method = PaymentMethod.objects.filter(active_status=1)

    if invoicing.finished_status == 1:
        messages.warning(request,_('Invoice is closed and cannot be edited.'))
        return redirect('isis:invoicing_list')

    if request.method == "POST":
        data = dict(request.POST)

        print(data)
        
        # Sum all values of payment inputs
        t = sum([Decimal(i) for i in data['amount']])

        if t < Decimal(invoicing.total):
            messages.error(request, _('Paid amount is less than total, it must be equal to total amount.'))
            return redirect('isis:document_payment', pk=pk)
        
        # We a going to use date_modified for payment date
        Invoicing.objects.filter(id=invoicing.id).update(date_modified= datetime.datetime.now(), 
        finished_status=1, paid_status=1, debit=0, credit=invoicing.total)

        if invoicing.bank_account is not None:
            save_bank_account(request, invoicing.bank_account, 0, invoicing.total, _("Invoicing") + 
            " " + str(invoicing.number))

        t = 0
        for x in data['payment_id']:
            save_payment_history(data['amount'][t], data['notes'][t], data['file'][t], 
            invoicing, x)
            t += 1

        if request.POST.get('show'):
            return redirect('isis:invoicing_show', pk=pk)
        else:
            return redirect('isis:invoicing_show_pos', pk=pk)

    context = {}
    context['invoicing'] = invoicing
    context['payment_method'] = payment_method

    return render(request, 'isis/modals/document_payment_modal.html', context)


@login_required
def product_return_create_view(request, pk):
    invoicing = Invoicing.objects.filter(pk=pk, ).first()

    if not invoicing:
        return False

    # If document is not finished product return cannot be created
    if invoicing.is_finished() == False:
        messages.warning(request,_('Document is not finished. Please Finish it First.'))
        return redirect('isis:invoicing_details', pk=pk)
    
    # If document does not modify stock product return cannot be created
    if invoicing.document.modify_stock == 0:
        messages.warning(request,_('Document does not modify stock.'))
        return redirect('isis:invoicing_details', pk=pk)

    number = increment_invoice_number(ProductReturn)
    name = _('Return Note') + str(number)
    slug = slugify(name)
    date = datetime.datetime.now()
    due_date = date
    paid_status = delivered_status = active_status = 1
    created_by = request.user

    product_return = ProductReturn(invoicing=invoicing, paid_status=paid_status, number=number,
    slug=slug, date=date, due_date=due_date, delivered_status=delivered_status, finished_status=0,
    active_status=active_status, date_created=date, date_modified=date, created_by=created_by,
    bank_account=invoicing.bank_account, name=name)

    product_return.save()

    # Copy Items from Invoicing
    items = InvoicingItem.objects.filter(invoicing=invoicing)
    for product in items:
        save_return_product_details(product, product_return)

    return redirect('isis:product_return_item_create', pk=product_return.pk)


@login_required
def product_return_update_view(request, pk):
    product_return = ProductReturn.objects.filter(pk=pk, ).first()

    return redirect('isis:product_return_item_create', pk=product_return.pk)

def save_return_product_details(product, product_return):
    tax = product.tax
    discount = product.discount
    price = product.price
    quantity = product.quantity
    tax_total = product.tax_total
    discount_total = product.discount_total
    sub_total = product.sub_total
    total = product.total
    product_id = product.product.id
    product_return_id = product_return.id 

    pr = ProductReturnItem(tax=tax, discount=discount, price=price,
    quantity=quantity, tax_total=tax_total, discount_total=discount_total, 
    sub_total=sub_total, total=total, product_id=product_id, 
    product_return_id=product_return_id)

    pr.save()


@login_required
def product_return_list_view(request):

    start_date = datetime.datetime.now() - datetime.timedelta(days=30)
    end_date = datetime.datetime.now() + datetime.timedelta(days=1)

    if request.method == "POST":
        search_form = StockSearchForm(request.POST)
        start_date = request.POST.get("start_date".replace('T', " "))
        end_date = request.POST.get("end_date")

        product_return = ProductReturn.objects.raw("""
        SELECT inv.*, SUM(item.discount_total) AS ds, SUM(item.sub_total) AS sb, 
        SUM(item.tax_total) AS tax, SUM(item.total) AS tt 
        FROM isis_productreturn AS inv
        LEFT JOIN isis_productreturnitem item ON inv.id=item.product_return_id
        WHERE inv.date_created BETWEEN '{}' AND '{}'
        GROUP BY inv.id  
        """.format(str(start_date).replace('T', " "), str(end_date).replace('T', " ")))
    else:
        search_form = StockSearchForm()
        product_return = ProductReturn.objects.raw("""
        SELECT inv.*, SUM(item.discount_total) AS ds, SUM(item.sub_total) AS sb, 
        SUM(item.tax_total) AS tax, SUM(item.total) AS tt 
        FROM isis_productreturn AS inv
        LEFT JOIN isis_productreturnitem item ON inv.id=item.product_return_id
        WHERE inv.date_created BETWEEN '{}' AND '{}'
        GROUP BY inv.id  """.format(start_date, end_date))
    
    context = {}
    context['search_form'] = search_form
    context['object_list'] = product_return

    return render(request, 'isis/listviews/product_return_list.html', context) 


@login_required
def product_return_item_create_view(request, pk):
    """
    Creates or Adds ProductReturn Items
    """
    product_return = get_object_or_404(ProductReturn, pk=pk)
    
    print(product_return.finished_status, product_return.id)

    if product_return.is_finished():
        messages.warning(request,_('Document is closed and cannot be edited.'))
        return redirect('isis:invoicing_list')

    items = ProductReturnItem.objects.filter(product_return=product_return)

    tax_total = items.aggregate(tax=Coalesce(Sum('tax_total'), V(0), output_field=DecimalField()))
    discount_total = items.aggregate(discount=Coalesce(Sum('discount_total'), V(0), output_field=DecimalField()))
    sub_total = items.aggregate(subtotal=Coalesce(Sum('sub_total'), V(0), output_field=DecimalField()))
    total = items.aggregate(total=Coalesce(Sum('total'), V(0), output_field=DecimalField()))

    if request.method == 'POST':
        form = ProductReturnItemForm(request.POST)

        if request.POST.get('validate'):
            document = '{} - {}'.format(_('Return Note'), product_return.id)

            # Prevent Finishing Empty Invoice 
            if not items:
                messages.warning(request, _("Please create Invoice Items First"))
                return redirect('isis:product_return_item_create', pk=pk)

            # Records stock movement 
            if product_return.finished_status == 0:
                for i in items:
                    manage_stock(request, document, i.product, i.quantity, product_return.warehouse, product_return.costumer, 
                "Product Return")
    
            # Changes the ProductReturn status to finished_status
            inv = ProductReturn.objects.filter(id=product_return.id).update(finished_status=1, 
            delivered_status=1)
            return redirect('isis:product_return_show', pk=pk)         
        else:
            # Records a line to ProductReturn
            warehouse = product_return.warehouse

            if request.POST.get('barcode') != '':
                product = Product.objects.filter(Q(code=str(request.POST.get('barcode'))) |
                Q(barcode=str(request.POST.get('barcode')))).first()

                if product:
                    name = product.id
                    quantity = Decimal(1)
                    tax = product.tax.id
                    discount = Decimal(0)
                    price = product.sell_price
                    product_object = get_or_save_product(request, name, tax, warehouse)
                else:
                    messages.warning(request, _("No product matches the given barcode. Please choose product from the dropdown below."))
                    return redirect('isis:product_return_item_create', pk=pk)
            else:
                try:
                    name = request.POST.get('product')
                    quantity = Decimal(request.POST.get('quantity'))
                    tax = Decimal(request.POST.get('tax'))
                    discount = Decimal(request.POST.get('discount'))
                    price = Decimal(request.POST.get('price'))

                    product_object = get_or_save_product(request, name, tax, warehouse)
                    
                except Exception as e:
                    messages.warning(request, _("Please use numbers that do not contain commas (','), and use dot ('.') for decimals.\n{}.".format(e)))
                    return redirect('isis:product_return_item_create', pk=pk)
    
            if not product_object:
                messages.warning(request, _("Please choose product from the dropdown, or add a new product."))
                return redirect('isis:product_return_item_create', pk=pk)

            if product_object.is_inactive:
                messages.warning(request, _("This product is inactive and cannot be sold.".format(e)))
                return redirect('isis:product_return_item_create', pk=pk)
            
            if product_object.is_not_for_sale:
                messages.warning(request, _("This product is not for sale.".format(e)))
                return redirect('isis:product_return_item_create', pk=pk)

            # save the data and after fetch the object in instance
            tax = Tax.objects.filter(id=int(tax)).first()
            instance = ProductReturnItem(product_return=product_return, tax=tax.rate, quantity=quantity,
            discount= discount, price=price, product=product_object) 
            instance.save()
            
            increase_decrease_product_return_totals(product_return.id)

        return redirect('isis:product_return_item_create', pk=pk)
    else:
        form = ProductReturnItemForm(None)
        return render(request, 'isis/createviews/product_return_item_create.html', 
        {'product_return': product_return, 'form': form, 'items': items, 'tax_total': tax_total, 
        'discount_total': discount_total, 'sub_total': sub_total, 'total': total})


@login_required
def product_return_item_delete_view(request):
    
    if request.is_ajax():
        selected_ids = request.POST['check_box_item_ids']
        selected_ids = json.loads(selected_ids)
        
        print(selected_ids)
        if len(selected_ids) == 1 and selected_ids[0] == 'None':
            return redirect('isis:product_return_item_create')

        if len(selected_ids) > 1:
            item = ProductReturn.objects.filter(id=int(selected_ids[1])).first()
        else:
            item = ProductReturn.objects.filter(id=int(selected_ids[0])).first()

        try:
            ProductReturn.objects.filter(id__in=selected_ids).delete()
            increase_decrease_product_return_totals(item.product_return_id)
        except Exception as e:
            messages.warning(request, _("Not Deleted! {}.".format(e)))
            print(e)
            return redirect('isis:product_return_create')
        return redirect('isis:product_return_create')


@login_required
def product_return_show(request, pk):
    """
    Displays ProductReturn for printing, export, ...
    """
    product_return = get_object_or_404(ProductReturn, pk=pk)
    items = ProductReturnItem.objects.filter(product_return=product_return)

    if request.method == 'POST':
        create_pdf

    tax_total = items.aggregate(Sum('tax_total'))
    discount_total = items.aggregate(Sum('discount_total'))
    sub_total = items.aggregate(Sum('sub_total'))
    total = items.aggregate(Sum('total'))

    costumer = Costumer.objects.get(id=product_return.costumer.id)
    company = Settings.objects.first()

    context = {'product_return': product_return, 'items': items, 'tax_total': tax_total, 
    'discount_total': discount_total, 'sub_total': sub_total, 
    'total': total, 'costumer': costumer, 'company': company}

    instance = ProductReturn.objects.filter(id=product_return.id).update(finished_status=1)
    return render(request, 'isis/documents/product_return.html', context) 


@login_required
def product_return_detail_view(request, pk):
    # dictionary for initial data with
    # field names as keys
    product_return = get_object_or_404(ProductReturn, pk=pk)

    paid_product_returns = ProductReturn.objects.filter(costumer=product_return.costumer, 
    paid_status=1).exclude(id=product_return.id).order_by('-number')[:5]
    
    overdue_product_returns = ProductReturn.objects.filter(costumer=product_return.costumer, 
    paid_status=0, due_date__lt=datetime.datetime.now()).exclude(id=product_return.id).order_by('number')
    
    not_paid_product_returns = ProductReturn.objects.filter(costumer=product_return.costumer, 
    paid_status=0).exclude(id=product_return.id).order_by('number')
    
    context ={}
    # add the dictionary during initialization
    context["product_return"] = product_return    
    context["paid_product_returns"] = paid_product_returns     
    context["not_paid_product_returns"] = not_paid_product_returns     
    context["overdue_product_returns"] = overdue_product_returns     

    return render(request, "isis/detailviews/product_return_detail_view.html", context)

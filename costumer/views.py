# -*- coding: utf-8 -*-
import datetime
import json
from decimal import Decimal
import sys
import os

from django.db.models import Sum, Value as V, DecimalField, Q
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
from config.settings import MEDIA_URL
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.http import JsonResponse
from django.core import serializers
from django.conf import settings
from django.contrib.staticfiles.finders import find
from django.templatetags.static import static

from utilities.utilities import increment_invoice_number

from .models import (CostumerInvoice, CostumerInvoiceItem, CostumerReceipt, CostumerReceiptInvoice)
from isis.models import (Costumer, Tax, Product)
from isis.forms import (PaymentTermForm, PaymentMethodForm)
from isis.views import get_or_save_product, manage_stock
from .forms import (CostumerInvoiceForm, CostumerInvoiceItemForm, CostumerForm, CostumerReceiptForm)
from asset_app.models import (Costumer, Settings)
from warehouse.forms import WarehouseForm
from stock.forms import StockSearchForm
from bank.models import BankAccount
from bank.forms import BankAccountForm

from utilities.utilities import make_payment, save_bank_account

########################## Costumer ##########################
class CostumerListView(LoginRequiredMixin, ListView):
    queryset = Costumer.objects.filter(is_costumer=1)
    template_name = 'costumer/listviews/costumer_list_view.html'


class CostumerCreateView(LoginRequiredMixin, CreateView):
    form_class = CostumerForm
    template_name = 'costumer/createviews/costumer_create.html'

    def form_valid(self, form):
        instance = form.save(commit=False)
        parent = self.request.POST.get('parent')
        
        if parent == "":
            instance.parent = 0
        else:
            instance.parent = parent

        instance.created_by = instance.modified_by = self.request.user
        instance.date_created = instance.date_modified = datetime.datetime.now()
        instance.is_costumer = 1
        instance = instance.save()
        messages.success(self.request, _("Costumer added successfully!"))

        if self.request.POST.get('save_costumer'):
            return redirect('costumer:costumer_list')
        else:
            return redirect('costumer:costumer_create')

    def form_invalid(self, form):
        print(form.errors)
        for error in form.errors.values():
            messages.error(self.request, error)
        return redirect('costumer:costumer_create')


class CostumerUpdateView(LoginRequiredMixin, UpdateView):
    form_class = CostumerForm
    model = Costumer
    template_name = 'costumer/updateviews/costumer_update.html'

    def form_valid(self, form):
        instance = form.save(commit=False)
        parent = self.request.POST.get('parent')
    
        if parent == "":
            instance.parent = 0
        else:
            instance.parent = parent
            if int(parent) == self.get_object().pk:
                messages.warning(self.request, _("Parent Costumer and Costumer must be different!"))
                return redirect('costumer:costumer_update', self.get_object().pk)

        instance.created_by = instance.modified_by = self.request.user
        instance.date_modified = datetime.datetime.now()
        instance.is_costumer = 1
        instance = instance.save()
        messages.success(self.request, _("Costumer updated successfully!"))

        if self.request.POST.get('save_costumer'):
            return redirect('costumer:costumer_list')
        else:
            return redirect('costumer:costumer_create')

    def form_invalid(self, form):
        print(form.errors)
        for error in form.errors.values():
            messages.error(self.request, error)
        return redirect('costumer:costumer_update', self.get_object().pk)


@login_required
def costumer_delete_view(request):
    if request.is_ajax():
        selected_ids = request.POST['check_box_item_ids']
        selected_ids = json.loads(selected_ids)
        for i, id in enumerate(selected_ids):
            if id != '':
                try:
                    Costumer.objects.filter(id__in=selected_ids).delete()
                except Exception as e:
                    messages.warning(request, _("Not Deleted! {}".format(e)))
                    return redirect('costumer:costumer_list')
        
        messages.warning(request, _("Costumer delete successfully!"))
        return redirect('costumer:costumer_list')


class CostumerDetailView(LoginRequiredMixin, DetailView):
    model = Costumer
    template_name = 'costumer/detailviews/costumer_detail_view.html'

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        context['data'] = self.get_object()

        return context


@login_required
def invoice_list_view(request):

    start_date = datetime.datetime.now() - datetime.timedelta(days=30)
    end_date = datetime.datetime.now() + datetime.timedelta(hours=5)

    if request.method == "POST":
        search_form = StockSearchForm(request.POST)
        start_date = request.POST.get("start_date")
        end_date = request.POST.get("end_date")

        invoice = CostumerInvoice.objects.raw("""
        SELECT inv.*, SUM(item.discount_total) AS ds, SUM(item.sub_total) AS sb, 
        SUM(item.tax_total) AS tax, SUM(item.total) AS tt 
        FROM costumer_costumerinvoice AS inv
        LEFT JOIN costumer_costumerinvoiceitem item ON inv.id=item.invoice_id
        WHERE inv.date_created BETWEEN '{}' AND '{}'
        GROUP BY inv.id  
        """.format(str(start_date).replace('T', " "), str(end_date).replace('T', " ")))
    else:
        search_form = StockSearchForm()
        invoice = CostumerInvoice.objects.raw("""
        SELECT inv.*, SUM(item.discount_total) AS ds, SUM(item.sub_total) AS sb, 
        SUM(item.tax_total) AS tax, SUM(item.total) AS tt 
        FROM costumer_costumerinvoice AS inv
        LEFT JOIN costumer_costumerinvoiceitem item ON inv.id=item.invoice_id
        WHERE inv.date_created BETWEEN '{}' AND '{}'
        GROUP BY inv.id  """.format(start_date, end_date))
    
    context = {}
    context['search_form'] = search_form
    context['object_list'] = invoice

    return render(request, 'costumer/listviews/invoice_list.html', context) 

    
@login_required
def invoice_show(request, pk):
    """
    Displays CostumerInvoice for printing, export, ...
    """
    invoice = get_object_or_404(CostumerInvoice, pk=pk)
    items = CostumerInvoiceItem.objects.filter(invoice=invoice)

    tax_total = items.aggregate(Sum('tax_total'))
    discount_total = items.aggregate(Sum('discount_total'))
    sub_total = items.aggregate(Sum('sub_total'))
    total = items.aggregate(Sum('total'))

    costumer = Costumer.objects.get(id=invoice.costumer.id)
    company = Settings.objects.first()

    context = {'invoice': invoice, 'items': items, 'tax_total': tax_total, 
    'discount_total': discount_total, 'sub_total': sub_total, 
    'total': total, 'costumer': costumer, 'company': company}

    instance = CostumerInvoice.objects.filter(id=invoice.id).update(finished_status=1)
    return render(request, 'costumer/documents/invoice.html', context) 


# increments numbering in docs ex: Invoice, Receipt, and so on
def increment_number(model):
    # Returns the first object matched by the queryset, or None if there is no matching object. 
    i = model.objects.order_by('-id').first()
    if i is not None:
        document_number = i.number + 1
    else:
        document_number = 1

    return document_number


@login_required
def invoice_create_view(request):
    if request.method == 'POST':
        form = CostumerInvoiceForm(request.POST)
        costumer_form = CostumerForm(request.POST)
        warehouse_form = WarehouseForm(request.POST)
        payment_term_form = PaymentTermForm(request.POST)
        payment_method_form = PaymentMethodForm(request.POST)
        bank_account_form = BankAccountForm(request.POST)

        if request.POST.get('save_bank_account_new') or request.POST.get('save_bank_account'):
            if bank_account_form.is_valid():        
                instance = bank_account_form.save(commit=False)
                instance.created_by = instance.modified_by = request.user
                instance.date_created = instance.date_modified = datetime.datetime.now()
                instance = instance.save()
                return redirect('costumer:costumer_invoice_create')
            else:
                for error in bank_account_form.errors.values():
                    messages.error(request, error)
                return redirect('costumer:costumer_invoice_create')
        
        if request.POST.get('save_payment_method_new') or request.POST.get('save_payment_method'):
            if payment_method_form.is_valid():        
                instance = payment_method_form.save(commit=False)
                instance.created_by = instance.modified_by = request.user
                instance.date_created = instance.date_modified = datetime.datetime.now()
                instance = instance.save()
                return redirect('costumer:costumer_invoice_create')
            else:
                for error in payment_method_form.errors.values():
                    messages.error(request, error)
                return redirect('costumer:costumer_invoice_create')

        if request.POST.get('save_payment_term_new') or request.POST.get('save_payment_term'):
            if payment_term_form.is_valid():        
                instance = payment_term_form.save(commit=False)
                instance.created_by = instance.modified_by = request.user
                instance.date_created = instance.date_modified = datetime.datetime.now()
                instance = instance.save()
                return redirect('costumer:costumer_invoice_create')
            else:
                print(payment_term_form.errors)
                for error in payment_term_form.errors.values():
                    messages.error(request, error)
                return redirect('costumer:costumer_invoice_create')

        if request.POST.get('save_costumer_new') or request.POST.get('save_costumer'):
            if costumer_form.is_valid():        
                instance = costumer_form.save(commit=False)
                parent = request.POST.get('parent')
                if parent == "":
                    instance.parent = 0
                else:
                    instance.parent = parent
                instance.created_by = instance.modified_by = request.user
                instance.date_created = instance.date_modified = datetime.datetime.now()
                instance.is_costumer = 1
                instance = instance.save()
                return redirect('costumer:costumer_invoice_create')
            else:
                for error in costumer_form.errors.values():
                    messages.error(request, error)
                return redirect('costumer:costumer_invoice_create')

        if request.POST.get('save_warehouse_new') or request.POST.get('save_warehouse'):
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
                return redirect('costumer:costumer_invoice_create')
            else:
                for error in warehouse_form.errors.values():
                    messages.error(request, error)
                return redirect('costumer:costumer_invoice_create')

        if form.is_valid():
            instance = form.save(commit=False)
            instance.created_by = instance.modified_by = request.user
            instance.date_created = instance.date_modified = datetime.datetime.now()
            
            document_number = increment_number(CostumerInvoice)

            instance.number = document_number
            invoice = instance
            instance = instance.save()
            
            pk = invoice.id
            
            return redirect('costumer:costumer_invoice_item_create', pk=pk)

        else:
            for error in form.errors.values():
                messages.error(request, error)
            return redirect('costumer:costumer_invoice_create')
    else:
        form = CostumerInvoiceForm()
        costumer_form = CostumerForm()
        warehouse_form = WarehouseForm()
        payment_term_form = PaymentTermForm()
        payment_method_form = PaymentMethodForm()
        bank_account_form = BankAccountForm()

        context = {'form': form, 'costumer_form': costumer_form, 
        'warehouse_form': warehouse_form, 'payment_term_form': payment_term_form,
        'payment_method_form': payment_method_form, 'bank_account_form': bank_account_form}
        return render(request, 'costumer/createviews/invoice_create.html', context)


@login_required
def invoice_update_view(request, pk):
    invoice = get_object_or_404(CostumerInvoice, pk=pk)
    invoice_number = invoice.number
    form = CostumerInvoiceForm(request.POST or None, instance=invoice)
    costumer_form = CostumerForm(request.POST or None)
    warehouse_form = WarehouseForm(request.POST or None)
    payment_term_form = PaymentTermForm(request.POST or None)
    payment_method_form = PaymentMethodForm(request.POST or None)
    bank_account_form = BankAccountForm(request.POST or None)

    if request.method == 'POST':

        if request.POST.get('save_bank_account_new') or request.POST.get('save_bank_account'):
            if bank_account_form.is_valid():        
                instance = bank_account_form.save(commit=False)
                instance.created_by = instance.modified_by = request.user
                instance.date_created = instance.date_modified = datetime.datetime.now()
                instance = instance.save()
                return redirect('costumer:costumer_invoice_create')
            else:
                for error in bank_account_form.errors.values():
                    messages.error(request, error)
                return redirect('costumer:costumer_invoice_create')
        
        if request.POST.get('save_payment_method_new') or request.POST.get('save_payment_method'):
            if payment_method_form.is_valid():        
                instance = payment_method_form.save(commit=False)
                instance.created_by = instance.modified_by = request.user
                instance.date_created = instance.date_modified = datetime.datetime.now()
                instance = instance.save()
                return redirect('costumer:costumer_invoice_create')
            else:
                for error in payment_method_form.errors.values():
                    messages.error(request, error)
                return redirect('costumer:costumer_invoice_create')

        if request.POST.get('save_payment_term_new') or request.POST.get('save_payment_term'):
            if payment_term_form.is_valid():        
                instance = payment_term_form.save(commit=False)
                instance.created_by = instance.modified_by = request.user
                instance.date_created = instance.date_modified = datetime.datetime.now()
                instance = instance.save()
                return redirect('costumer:costumer_invoice_create')
            else:
                for error in payment_term_form.errors.values():
                    messages.error(request, error)
                return redirect('costumer:costumer_invoice_create')

        if request.POST.get('save_costumer_new') or request.POST.get('save_costumer'):
            if costumer_form.is_valid():        
                instance = costumer_form.save(commit=False)
                instance.created_by = instance.modified_by = request.user
                instance.date_created = instance.date_modified = datetime.datetime.now()
                instance.is_costumer = 1
                parent = request.POST.get('parent')
                if parent == "":
                    instance.parent = 0
                else:
                    instance.parent = parent
                instance = instance.save()
                return redirect('costumer:costumer_invoice_create')
            else:
                for error in costumer_form.errors.values():
                    messages.error(request, error)
                return redirect('costumer:costumer_invoice_create')

        if request.POST.get('save_warehouse_new') or request.POST.get('save_warehouse'):
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
                return redirect('costumer:costumer_invoice_create')
            else:
                for error in warehouse_form.errors.values():
                    messages.error(request, error)
                return redirect('costumer:costumer_invoice_create')

        if form.is_valid():
            instance = form.save(commit=False)
            instance.modified_by = request.user
            
            instance.date_modified = datetime.datetime.now()
            instance.number = invoice_number
            instance = instance.save()
            return redirect('costumer:costumer_invoice_item_create', pk=pk)

        else:
            for error in form.errors.values():
                messages.error(request, error)
            return redirect('costumer:costumer_invoice_update', pk=pk)

    context = {'form': form, 'costumer_form': costumer_form, 'warehouse_form': warehouse_form, 
    'payment_term_form': payment_term_form,'payment_method_form': payment_method_form,
    'bank_account_form': bank_account_form}

    return render(request, 'costumer/updateviews/invoice_update.html', context)


@login_required
def invoice_delete_view(request):
    if request.is_ajax():
        selected_ids = request.POST['check_box_item_ids']
        selected_ids = json.loads(selected_ids)
        for i, id in enumerate(selected_ids):
            if id != '':
                try:
                    CostumerInvoice.objects.filter(id__in=selected_ids).delete()
                    # Set parent to No parent in invoices with deleted parents
                    CostumerInvoice.objects.filter(parent__in=selected_ids).update(parent=0)
                except Exception as e:
                    messages.warning(request, _("Not Deleted! {}".format(e)))
                    return redirect('costumer:costumer_invoice_list')
        
        messages.warning(request, _("Costumer Invoice delete successfully!"))
        return redirect('costumer:costumer_invoice_list')


def invoice_dashboard_view(request):
    ROUTINE = 'Routine'
    PREVENTIVE = 'Preventive'
    CORRECTIVE = 'Corrective'
    PREDECTIVE = 'Predective'

    last_invoices =  CostumerInvoice.objects.all().order_by('-date_created')[:15]
    total_invoices =  CostumerInvoice.objects.all().count()
    all_invoices = CostumerInvoice.objects.all().order_by('name')
    
    context = {}
    context['total'] = total_invoices
    context['last'] = last_invoices
    context['all'] = all_invoices
    
    return render(request, 'costumer/dashboardviews/invoice_dashboard.html', context=context)

@login_required
def invoice_detail_view(request, pk):
    # dictionary for initial data with
    # field names as keys
    invoice = get_object_or_404(CostumerInvoice, pk=pk)

    paid_invoices = CostumerInvoice.objects.filter(costumer=invoice.costumer, 
    paid_status=1).exclude(id=invoice.id).order_by('-number')[:5]
    
    overdue_invoices = CostumerInvoice.objects.filter(costumer=invoice.costumer, 
    paid_status=0, due_date__lt=datetime.datetime.now()).exclude(id=invoice.id).order_by('number')
    
    not_paid_invoices = CostumerInvoice.objects.filter(costumer=invoice.costumer, 
    paid_status=0).exclude(id=invoice.id).order_by('number')
    
    context ={}
    # add the dictionary during initialization
    context["invoice"] = invoice    
    context["paid_invoices"] = paid_invoices     
    context["not_paid_invoices"] = not_paid_invoices     
    context["overdue_invoices"] = overdue_invoices     
    return render(request, "costumer/detailviews/invoice_detail_view.html", context)


@login_required
def invoice_item_create_view(request, pk):
    """
    Creates or Adds CostumerInvoice Items
    """
    invoice = get_object_or_404(CostumerInvoice, pk=pk)
    
    if invoice.is_finished:
        messages.warning(request,_('Costumer Invoice is closed and cannot be edited.'))
        return redirect('costumer:costumer_invoice_list')

    items = CostumerInvoiceItem.objects.filter(invoice=invoice)

    tax_total = items.aggregate(tax=Coalesce(Sum('tax_total'), V(0), output_field=DecimalField()))
    discount_total = items.aggregate(discount=Coalesce(Sum('discount_total'), V(0), output_field=DecimalField()))
    sub_total = items.aggregate(subtotal=Coalesce(Sum('sub_total'), V(0), output_field=DecimalField()))
    total = items.aggregate(total=Coalesce(Sum('total'), V(0), output_field=DecimalField()))

    if request.method == 'POST':
        form = CostumerInvoiceItemForm(request.POST)

        if request.POST.get('validate'):
            if form.is_valid():
                document = '{} - {}'.format(_('CostumerInvoice'), invoice.id)

                # Prevent Finishing Empty Invoice 
                if not items:
                    messages.warning(request, _("Please create Invoice Items First"))
                    return redirect('costumer:costumer_invoice_item_create', pk=pk)

                # Records stock movement 
                if invoice.finished_status == 0:
                    for i in items:
                        manage_stock(request, document, i.product, -i.quantity, invoice.warehouse, invoice.costumer, 
                    "Costumer Invoice")
                
                # Changes the CostumerInvoice status to finished_status
                inv = CostumerInvoice.objects.filter(id=invoice.id).update(finished_status=1)
                invoice_show(request, pk)
                if invoice.bank_account is not None:
                    save_bank_account(request, invoice.bank_account, 0, invoice.total, _("Invoice") + " " 
                    + {str(invoice.number)})

                return redirect('costumer:costumer_invoice_show', pk=pk)
            else:
                print(form.errors)
                for error in form.errors.values():
                    messages.error(request, error)
                return redirect('costumer:costumer_invoice_show', pk=pk)

        else:
            # Records a line to CostumerInvoice
            warehouse = invoice.warehouse

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
                    return redirect('costumer:costumer_invoice_item_create', pk=pk)
            else:
                try:
                    name = request.POST.get('product')
                    quantity = Decimal(request.POST.get('quantity'))
                    tax = Decimal(request.POST.get('tax'))
                    print(tax, type(tax))
                    discount = Decimal(request.POST.get('discount'))
                    price = Decimal(request.POST.get('price'))

                    product_object = get_or_save_product(request, name, tax, warehouse)
                    
                except Exception as e:
                    messages.warning(request, _("Please use numbers that do not contain commas (','), and use dot ('.') for decimals.\n{}.".format(e)))
                    return redirect('costumer:costumer_invoice_item_create', pk=pk)
                
            if not product_object:
                messages.warning(request, _("Please choose product from the dropdown, or add a new product."))
                return redirect('costumer:costumer_invoice_item_create', pk=pk)

            if product_object.is_inactive:
                messages.warning(request, _("This product is inactive and cannot be sold.".format(e)))
                return redirect('costumer:costumer_invoice_item_create', pk=pk)
            
            if product_object.is_not_for_sale:
                messages.warning(request, _("This product is not for sale.".format(e)))
                return redirect('costumer:costumer_invoice_item_create', pk=pk)

            # save the data and after fetch the object in instance
            tax = Tax.objects.filter(id=int(tax)).first()
            instance = CostumerInvoiceItem(invoice=invoice, tax=tax.rate, quantity=quantity,
            discount= discount, price=price, product=product_object) 
            instance.save()
            
            increase_decrease_invoice_totals(invoice.id)

        return redirect('costumer:costumer_invoice_item_create', pk=pk)
    else:
        form = CostumerInvoiceItemForm(None)
        return render(request, 'costumer/createviews/invoice_item_create.html', 
        {'invoice': invoice, 'form': form, 'items': items, 'tax_total': tax_total, 
        'discount_total': discount_total, 'sub_total': sub_total, 'total': total})


def increase_decrease_invoice_totals(invoice_id):
    """
    Modifies (Decreases or increases) CostumerInvoice totals when item is deleted
    """

    items = CostumerInvoiceItem.objects.filter(invoice=invoice_id)

    tax_total = items.aggregate(tax=Coalesce(Sum('tax_total'), V(0), output_field=DecimalField()))
    discount_total = items.aggregate(discount=Coalesce(Sum('discount_total'), V(0), output_field=DecimalField()))
    sub_total = items.aggregate(subtotal=Coalesce(Sum('sub_total'), V(0), output_field=DecimalField()))
    total = items.aggregate(total=Coalesce(Sum('total'), V(0), output_field=DecimalField()))

    inv = CostumerInvoice.objects.filter(id=invoice_id).update(
    debit=total['total'],
    total=total['total'],
    subtotal=sub_total['subtotal'],
    total_tax=tax_total['tax'],
    total_discount=discount_total['discount']
    )

    return inv


@login_required
def invoice_item_delete_view(request):
    if request.is_ajax():
        selected_ids = request.POST['check_box_item_ids']
        selected_ids = json.loads(selected_ids)
        print(selected_ids)

        for i, id in enumerate(selected_ids):
            if id != '':
                try:
                    CostumerInvoiceItem.objects.filter(id__in=selected_ids).delete()
                except Exception as e:
                    messages.warning(request, _("Not Deleted! {}.".format(e)))
                    return redirect('costumer:costumer_invoice_create')

        return redirect('costumer:costumer_invoice_create')


class CostumerReceiptListView(LoginRequiredMixin, ListView):
    start_date = datetime.datetime.now() - datetime.timedelta(days=30)
    end_date = datetime.datetime.now()

    form_class = StockSearchForm
    queryset = CostumerReceipt.objects.filter(date_created__gte=start_date,
    date_created__lte=end_date)

    template_name = 'costumer/listviews/costumer_receipt_list.html'

    def post(self, request, *args, **kwargs):
        form = self.form_class

        start_date = self.request.POST.get('start_date')
        end_date = self.request.POST.get('end_date')

        if form.is_valid:
            self.queryset = CostumerReceipt.objects.filter(date_created__gte=start_date,
            date_created__lte=end_date)

            print(self.queryset.query)
            context = {}
            context['object_list'] = self.queryset
            form = self.form_class
            context['search_form'] = form

            return render(self.request, self.template_name, context)
        else:
            for error in form.errors.values():
                messages.error(request, error)
            return self.form_invalid(form)

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        context['object_list'] = self.queryset
        print(self.queryset.query)
        form = self.form_class
        context['search_form'] = form

        return context


class ReceiptItemsCreateView(LoginRequiredMixin, UpdateView):
    model = CostumerReceipt
    template_name = 'costumer/createviews/costumer_receipt_invoice.html'
    fields = ['finished_status']
    
    def post(self, request):
        # converts django query dict to python dictionary
        # and creates a dictionary of invoices
        data = dict(request.POST)
        # Pick invoices key from dict
        invoices = data['invoices']
        
        t = 0
        for inv in invoices:
            payment = data['payment'][t]
            
            invoice = CostumerInvoice.objects.get(id=int(inv))

            # make_payment(receipt_invoice_model, invoice_model, receipt_object, invoice, payment)
            make_payment(CostumerReceiptInvoice, CostumerInvoice, self.get_object(), invoice, payment)
            
            t += 1

        # Check if there are items in invoice or not
        items = CostumerReceiptInvoice.objects.filter(receipt_id=self.get_object().pk)

        if len(items) == 0:
            messages.warning(request, _("Please enter at least one payment!"))
            return redirect('costumer:costumer_receipt_invoice', pk=self.get_object().pk)

        # Finish receipt
        self.get_object().update(finished_status=1)
        return redirect('costumer:costumer_receipt_show', pk=self.get_object().pk)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        costumer_receipt = self.get_object()
        invoices = CostumerInvoice.objects.filter(costumer=costumer_receipt.costumer,
        paid_status=0, active_status=1, finished_status=1).order_by('date_created')

        context['receipt'] = costumer_receipt
        context['invoices'] = invoices
        
        return context

    def get(self, request, *args, **kwargs):
        # If Receipt is in finished status quits and redirects to List of receipts
        if self.get_object().is_finished:
            messages.warning(request,_('Costumer Receipt is closed and cannot be edited.'))
            return redirect('costumer:costumer_receipt_list')

        # If Receipt is in finished status quits and redirects to List of receipts
        if self.get_object().is_inactive:
            messages.warning(request,_('Costumer Receipt is inactive and cannot be edited.'))
            return redirect('costumer:costumer_receipt_list')

        invoices = CostumerInvoice.objects.filter(costumer=self.get_object().costumer,
        paid_status=0, active_status=1, finished_status=1).order_by('date_created')

        # If there are no pending invoices returns to invoice List
        if not invoices:
            messages.warning(request, _("This costumer has no pending invoices!"))
            return redirect('costumer:costumer_receipt_list')


@login_required
def costumer_receipt_invoice_view(request, pk):
    '''
    Creates Receipt Items and Finalizes Receipts
    '''

    costumer_receipt = get_object_or_404(CostumerReceipt, pk=pk)

    # If Receipt is in finished status quits and redirects to List of receipts
    if costumer_receipt.is_finished:
        messages.warning(request,_('Costumer Receipt is closed and cannot be edited.'))
        return redirect('costumer:costumer_receipt_list')

    # If Receipt is in finished status quits and redirects to List of receipts
    if costumer_receipt.is_inactive:
        messages.warning(request,_('Costumer Receipt is inactive and cannot be edited.'))
        return redirect('costumer:costumer_receipt_list')

    invoices = CostumerInvoice.objects.filter(costumer=costumer_receipt.costumer,
    paid_status=0, active_status=1, finished_status=1).order_by('date_created')

    # If there are no pending invoices returns to invoice List
    if not invoices:
        messages.warning(request, _("This costumer has no pending invoices!"))
        return redirect('costumer:costumer_receipt_list')

    if request.method == 'POST':
        # converts django query dict to python dictionary
        # and creates a dictionary of invoices
        data = dict(request.POST)
        # Pick invoices key from dict
        invoices = data['invoices']
        
        t = 0
        for inv in invoices:
            payment = data['payment'][t]
            
            invoice = CostumerInvoice.objects.get(id=int(inv))

            # make_payment(receipt_invoice_model, invoice_model, receipt_object, invoice, payment)
            make_payment(CostumerReceiptInvoice, CostumerInvoice, costumer_receipt, invoice, payment)
            
            t += 1

        # Check if there are items in invoice or not
        items = CostumerReceiptInvoice.objects.filter(receipt_id=pk)

        if len(items) == 0:
            messages.warning(request, _("Please enter at least one payment!"))
            return redirect('costumer:costumer_receipt_invoice', pk=pk)

        # Finish receipt 
        CostumerReceipt.objects.filter(id=costumer_receipt.id).update(finished_status=1)
        return redirect('costumer:costumer_receipt_show', pk=pk)

    context = {'receipt': costumer_receipt, 'invoices': invoices}
    return render(request, 'costumer/createviews/costumer_receipt_invoice.html', context=context)

    
def check_costumer_invoices(costumer):
    '''
    # Checks weather costumer has pending Costumer Invoices or not
    '''
    invoices = CostumerInvoice.objects.filter(costumer_id=int(costumer),
    paid_status=0, active_status=1, finished_status=1).order_by('date_created')

    if not invoices:
        return False
    
    return True

@login_required
def costumer_receipt_create_view(request):
    
    if request.method == 'POST':
        costumer = request.POST.get('costumer')
        if not costumer:
            messages.warning(request, _("There are no invoices with pending payments! Please create Costumer Invoice First."))
            return redirect('costumer:costumer_invoice_create')
        
        costumer_invoices = check_costumer_invoices(costumer)

        # Checks weather costumer has pending CostumerInvoices or not
        if not costumer_invoices:
            messages.warning(request, _("This costumer has no pending invoices!"))
            return redirect('costumer:costumer_receipt_list')

        form = CostumerReceiptForm(request.POST)
        if form.is_valid():
            instance = form.save(commit=False)
            instance.created_by = instance.modified_by = request.user
            instance.date_created = instance.date_modified = datetime.datetime.now()
            instance.credit = 0
            instance.debit = 0

            document_number = increment_invoice_number(CostumerReceipt)

            instance.number = document_number
            receipt = instance
            instance = instance.save()

            pk = receipt.pk
            return redirect('costumer:costumer_receipt_invoice', pk=pk)
            
        else:
            print(form.errors)
            for error in form.errors.values():
                messages.error(request, error)
            return redirect('costumer:costumer_receipt_create')
    else:
        form = CostumerReceiptForm()
        context = {'form': form}
        return render(request, 'costumer/createviews/costumer_receipt_create.html', context)


@login_required
def costumer_receipt_update_view(request, pk):
    costumer_receipt = get_object_or_404(CostumerReceipt, pk=pk)
    form = CostumerReceiptForm(request.POST or None, instance=costumer_receipt)

    # If Receipt is in finished status quits and redirects to List of receipts
    if costumer_receipt.is_finished:
        messages.warning(request,_('Costumer Receipt is closed and cannot be edited.'))
        return redirect('costumer:costumer_receipt_list')

    # If Receipt is in finished status quits and redirects to List of receipts
    if costumer_receipt.is_inactive:
        messages.warning(request,_('Costumer Receipt is inactive and cannot be edited.'))
        return redirect('costumer:costumer_receipt_list')

    if request.method == 'POST':
        if form.is_valid():
            instance = form.save(commit=False)
            instance.modified_by = request.user
            instance.date_modified = datetime.datetime.now()
            instance = instance.save()
            
            return redirect('costumer:costumer_receipt_invoice', pk=pk)

        else:
            for error in form.errors.values():
                messages.error(request, error)
            return redirect('costumer:costumer_receipt_update', pk=pk)

    context = {'form': form}
    return render(request, 'costumer/updateviews/costumer_receipt_update.html', context)


@login_required
def costumer_receipt_delete_view(request):
    if request.is_ajax():
        selected_ids = request.POST['check_box_item_ids']
        selected_ids = json.loads(selected_ids)
        for i, id in enumerate(selected_ids):
            if id != '':
                try:
                    CostumerReceipt.objects.filter(id__in=selected_ids).delete()
                except Exception as e:
                    messages.warning(request, _("Not Deleted! {}".format(e)))
                    return redirect('costumer:costumer_receipt_list')
        
        messages.warning(request, _("Costumer Receipt delete successfully!"))
        return redirect('costumer:costumer_receipt_list')


@login_required
def costumer_receipt_detail_view(request, pk):
    costumer_receipt = get_object_or_404(CostumerReceipt, pk=pk)
    invoice_items = CostumerReceiptInvoice.objects.filter(receipt=costumer_receipt)

    # Field totals
    total = invoice_items.aggregate(total=Coalesce(Sum('debit'), V(0), output_field=DecimalField()))
    total_paid = invoice_items.aggregate(total=Coalesce(Sum('paid'), V(0), output_field=DecimalField()))
    total_debt = invoice_items.aggregate(total=Coalesce(Sum('remaining'), V(0), output_field=DecimalField()))

    context ={}
    # add the dictionary during initialization
    context["receipt"] = costumer_receipt    
    context["invoices"] = invoice_items
    context["total"] = total
    context["total_paid"] = total_paid
    context["total_debt"] = total_debt

    return render(request, "costumer/detailviews/costumer_receipt_detail_view.html", context)

@login_required
def costumer_receipt_show(request, pk):
    """
    Displays Receipt for printing, export, ...
    """
    receipt = get_object_or_404(CostumerReceipt, pk=pk)
    items = CostumerReceiptInvoice.objects.filter(receipt=receipt)

    total = items.aggregate(total=Coalesce(Sum('paid'), V(0), output_field=DecimalField()))

    costumer = Costumer.objects.get(id=receipt.costumer.id)
    company = Settings.objects.first()

    context = {'receipt': receipt, 'items': items,  
    'total': total, 'costumer': costumer, 'company': company}

    return render(request, 'costumer/documents/costumer_receipt.html', context) 

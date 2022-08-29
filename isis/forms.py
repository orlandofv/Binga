# -*- coding: utf-8 -*-
import datetime
from itertools import product
from math import prod

import sys

from django import forms
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Submit, Row, Column, Reset, HTML, Field
from crispy_forms.bootstrap import (FieldWithButtons, StrictButton, AccordionGroup, 
TabHolder, Tab, Div)
from django.utils.translation import ugettext_lazy as _
from crispy_bootstrap5.bootstrap5 import BS5Accordion

from .models import (Product, Gallery, Tax, Invoice, InvoiceItem, 
PaymentTerm, PaymentMethod, Receipt, Category, ReceiptInvoice, Document, 
Invoicing, InvoicingItem, ProductReturn, ProductReturnItem)
from warehouse.models import Warehouse
from django.utils import timezone
from users.models import User

from asset_app.fields import ListTextWidget
from asset_app.models import Costumer


class CategoryForm(forms.ModelForm):
    parent = forms.ModelChoiceField(label=_('Parent Category'), 
    queryset=Category.objects.filter(active_status=1), 
    required=False, initial=0)

    def __init__(self, *args, **kwargs):
        super(CategoryForm, self).__init__(*args, **kwargs)

        self.helper = FormHelper()
        self.helper.form_id = "category-form-id"
        self.helper.form_class = "category-form-class"
        self.helper.layout = Layout(
        HTML("""
            <p><strong style="font-size: 18px;">{}</strong></p>
            <hr>
        """.format(_('Add/Update Category'),)),
        BS5Accordion(
            AccordionGroup(_('CATEGORY MAIN DATA'),
                Row(
                    Column('name', css_class='form-group col-md-6 mb-0'),
                    Column('parent', css_class='form-group col-md-3 mb-0'),
                    Column('active_status', css_class='form-group col-md-3 mb-0'),
                    css_class='form-row'
                ),
                Row(
                    Column('image', css_class='form-group col-md-12 mb-0'),
                    css_class='form-row'),
                Row(
                    Column(Field('notes', rows='2'), css_class='form-group col-md-12 mb-0'),
                    css_class='form-row'),
            ),
                HTML('<br>'),
                Submit('save_category', _('Save & Close'), css_class='btn btn-primary fas fa-save'),
                Submit('save_category_new', _('Save & Edit'), css_class='btn btn-primary fas fa-save'),
                Reset('reset', 'Clear', css_class='btn btn-danger'),
                flush=True,
                always_open=True),
        )

    class Meta:
        model = Category
        exclude = ('date_created', 'date_modified', 'slug', 'created_by', 'modified_by')


    def clean_parent(self):
        pass


class ProductForm(forms.ModelForm):
    code = forms.CharField(max_length=50)
    name = forms.CharField(max_length=255)
    tax = forms.ModelChoiceField(queryset=Tax.objects.all(), initial=1)
    barcode = forms.CharField(max_length=255, required=False)
    sell_price = forms.DecimalField(label=_('Selling Price'), max_digits=18, decimal_places=6, initial=0, required=False)
    min_sell_price = forms.DecimalField(label=_('Min. Selling Price'),max_digits=18, decimal_places=6, initial=0, required=False)
    sell_price2 = forms.DecimalField(label=_('Selling Price 2'), max_digits=18, decimal_places=6, initial=0, required=False)
    sell_price3 = forms.DecimalField(label=_('Selling Price 3'), max_digits=18, decimal_places=6, initial=0, required=False)
    sell_price4 = forms.DecimalField(label=_('Selling Price 4'), max_digits=18, decimal_places=6, initial=0, required=False)
    sell_price5 = forms.DecimalField(label=_('Selling Price 5'), max_digits=18, decimal_places=6, initial=0, required=False)
    purchase_price = forms.DecimalField(label=_('Purchase Price'), max_digits=18, decimal_places=6, initial=0, required=False)
    physical_stock = forms.DecimalField(label=_('Purchase Price'), max_digits=18, decimal_places=6, initial=0, required=False)
    stock_limit = forms.DecimalField(label=_('Stock Limit'), max_digits=18, decimal_places=6, initial=0, required=False)
    desired_stock = forms.DecimalField(label=_('Desired Stock'), max_digits=18, decimal_places=6, initial=0, required=False)
    # product_nature = forms.CharField(max_length=50, choices=PRODUCT_NATURE, initial=RAW_PRODUCT)
    product_url = forms.URLField(max_length=255, required=False)
    weight = forms.DecimalField(max_digits=9, decimal_places=6, initial=0, required=False)
    length = forms.DecimalField(max_digits=9, decimal_places=6, initial=0, required=False)
    width = forms.DecimalField(max_digits=9, decimal_places=6, initial=0, required=False)
    height = forms.DecimalField(max_digits=9, decimal_places=6, initial=0, required=False)
    # length_units = forms.CharField(max_length=10, choices=LENGTH_CHOICES, initial=M)
    area = forms.DecimalField(max_digits=9, decimal_places=6, initial=0, required=False)
    # area_units = forms.CharField(max_length=10, choices=AREA_CHOICES, initial=M2)
    volume = forms.DecimalField(max_digits=9, decimal_places=6, initial=0, required=False)
    # volume_units = forms.CharField(max_length=10, choices=VOLUME_CHOICES, initial=0, required=False)
    # weight_units = forms.CharField(max_length=50, choices=WEIGHT_MEASUREMENT_CHOICES, initial=KG)
    # active_status = forms.IntegerField(choices=STATUSES, initial=ACTIVE)
    # sell_status = forms.IntegerField(choices=SELL_STATUSES, initial=FOR_SALE)
    # purchase_status = forms.IntegerField(choices=PURCHASE_STATUSES, initial=FOR_PURCHASE)
    images = forms.ImageField(label=_('Other Images'), required=False)

    def __init__(self, *args, **kwargs):
        super(ProductForm, self).__init__(*args, **kwargs)

        self.helper = FormHelper()
        self.helper.form_id = "product-form-id"
        self.helper.form_class = "product-form-class"
        self.helper.layout = Layout(
        HTML("""
            <p><strong style="font-size: 18px;">{}</strong></p>
            <hr>
        """.format(_('Add/Update product'),)),
        TabHolder(
            Tab(_('PRODUCT MAIN DATA'),
                Row(
                    Column('code', css_class='form-group col-md-6 mb-0'),
                    Column('barcode', css_class='form-group col-md-4 mb-0'),
                    Column('type', css_class='form-group col-md-2 mb-0'),
                    css_class='form-row'),
                Row(
                    Column('name', css_class='form-group col-md-6 mb-0'),
                    FieldWithButtons('category', StrictButton('',  css_class="btn fa fa-plus", 
                    data_bs_toggle="modal", data_bs_target="#category"), css_class='form-group col-md-3 mb-0'),
                    css_class='form-row'),
                Row(
                    Column('sell_price', css_class='form-group col-md-3 mb-0'),
                    Column('min_sell_price', css_class='form-group col-md-3 mb-0'),
                    FieldWithButtons('tax', StrictButton('',  css_class="btn fa fa-plus", 
                    data_bs_toggle="modal", data_bs_target="#tax"), css_class='form-group col-md-3 mb-0'),
                    FieldWithButtons('warehouse', StrictButton('',  css_class="btn fa fa-plus", 
                    data_bs_toggle="modal", data_bs_target="#warehouse"), css_class='form-group col-md-3 mb-0'),
                    css_class='form-row'),

                Row(
                    Column(Field('description', rows='2'), css_class='form-group col-md-12 mb-0'),
                    css_class='form-row'),
                Row(
                    Column('sell_status', css_class='form-group col-md-3 mb-0'),
                    Column('purchase_status', css_class='form-group col-md-3 mb-0'),
                    Column('active_status', css_class='form-group col-md-3 mb-0'),
                    Column('product_nature', css_class='form-group col-md-3 mb-0'),
                    css_class='form-row'),
                Row(
                    Column('product_url', css_class='form-group col-md-12 mb-0'),
                    css_class='form-row'),
            ),

            Tab(_('OTHER PRICES'),
                Row(
                    Column('sell_price2', css_class='form-group col-md-2 mb-0'),
                    Column('sell_price3', css_class='form-group col-md-2 mb-0'),
                    Column('sell_price4', css_class='form-group col-md-2 mb-0'),
                    Column('sell_price5', css_class='form-group col-md-2 mb-0'),
                    Column('purchase_price', css_class='form-group col-md-2 mb-0'),
                    Column('max_purchase_price', css_class='form-group col-md-2 mb-0'),
                    css_class='form-row'),
            ),

            Tab(_('IMAGES'),
                Row(
                    Column('image', css_class='form-group col-md-12 mb-0'),
                    css_class='form-row'),
                Row(
                    Column('images', css_class='form-group col-md-12 mb-0'),
                    css_class='form-row'),
            ),
            Tab(_('AREA - VOLUME - WEIGHT'),
                Row(
                    Column('length', css_class='form-group col-md-2 mb-0'),
                    Column('width', css_class='form-group col-md-2 mb-0'),
                    Column('height', css_class='form-group col-md-2 mb-0'),
                    Column('length_units', css_class='form-group col-md-2 mb-0'),
                    Column('weight', css_class='form-group col-md-2 mb-0'),
                    Column('weight_units', css_class='form-group col-md-2 mb-0'),
                    css_class='form-row'),
                Row(
                    Column('area', css_class='form-group col-md-3 mb-0'),
                    Column('area_units', css_class='form-group col-md-3 mb-0'),
                    Column('volume', css_class='form-group col-md-3 mb-0'),
                    Column('volume_units', css_class='form-group col-md-3 mb-0'),
                    css_class='form-row'),
            ),
            Tab(_('STOCKS'),
                Row(
                    Column('min_stock', css_class='form-group col-md-3 mb-0'),
                    Column('desired_stock', css_class='form-group col-md-3 mb-0'),
                    Column('stock_limit', css_class='form-group col-md-3 mb-0'),
                    css_class='form-row'),
            ),
            Tab(_('PRIVATE NOTES'),
                Row(
                    Column(Field('notes', rows='2'), css_class='form-group col-md-12 mb-0'),
                    css_class='form-row'),
            ),
        ),
         HTML('<br>'),
                Submit('save_product', _('Save & Close'), css_class='btn btn-primary fas fa-save'),
                Submit('save_product_new', _('Save & Edit'), css_class='btn btn-primary fas fa-save'),
                Reset('reset', 'Clear', css_class='btn btn-danger'),
        )

    def clean(self):
        cleaned_data = super().clean()

        code = cleaned_data.get('code')
        name = cleaned_data.get('name')
        
        if self.instance.pk:
            self.errors['code'] = self.error_class(_("""
            Product with same name already exists."""))

        if code == '':
            self.errors['code'] = self.error_class(_("""
            The Code of Product must not be empty."""))
    
        if name == '':
            self.errors['name'] = self.error_class(_("""
            The Name of Product must not be empty."""))
    
        return cleaned_data

    class Meta:
        model = Product
        exclude = ('date_created', 'date_modified', 'slug', 'created_by', 'modified_by')


class TaxForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(TaxForm, self).__init__(*args, **kwargs)

        self.helper = FormHelper()
        self.helper.form_id = "tax-form-id"
        self.helper.form_class = "tax-form-class"
        self.helper.layout = Layout(
        HTML("""
            <p><strong style="font-size: 18px;">{}</strong></p>
            <hr>
        """.format(_('Add/Update Tax'),)),
        BS5Accordion(
            AccordionGroup(_('TAX MAIN DATA'),
                Row(
                    Column('name', css_class='form-group col-md-6 mb-0'),
                    Column('rate', css_class='form-group col-md-3 mb-0'),
                    Column('active_status', css_class='form-group col-md-3 mb-0'),
                    css_class='form-row'
                ),
                Row(
                    Column(Field('notes', rows='2'), css_class='form-group col-md-12 mb-0'),
                    css_class='form-row'),
            ),
                HTML('<br>'),
                Submit('save_tax', _('Save & Close'), css_class='btn btn-primary fas fa-save'),
                Submit('save_tax_new', _('Save & Edit'), css_class='btn btn-primary fas fa-save'),
                Reset('reset', 'Clear', css_class='btn btn-danger'),
                flush=True,
                always_open=True),
        )

    class Meta:
        model = Tax
        exclude = ('date_created', 'date_modified', 'slug', 'created_by', 'modified_by')


class PaymentMethodForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(PaymentMethodForm, self).__init__(*args, **kwargs)

        self.helper = FormHelper()
        self.helper.form_id = "payment_method-form-id"
        self.helper.form_class = "payment_method-form-class"
        self.helper.layout = Layout(
        HTML("""
            <p><strong style="font-size: 18px;">{}</strong></p>
            <hr>
        """.format(_('Add/Update Payment Method'),)),
        BS5Accordion(
            AccordionGroup(_('PAYMENT METHOD DATA'),
                Row(
                    Column('name', css_class='form-group col-md-8 mb-0'),
                    Column('active_status', css_class='form-group col-md-4 mb-0'),
                    css_class='form-row'
                ),
                Row(
                    Column(Field('notes', rows='2'), css_class='form-group col-md-12 mb-0'),
                    css_class='form-row'),
            ),
                HTML('<br>'),
                Submit('save_payment_method', _('Save & Close'), css_class='btn btn-primary fas fa-save'),
                Submit('save_payment_method_new', _('Save & Edit'), css_class='btn btn-primary fas fa-save'),
                Reset('reset', 'Clear', css_class='btn btn-danger'),
                flush=True,
                always_open=True),
        )

    class Meta:
        model = PaymentMethod
        exclude = ('date_created', 'date_modified', 'slug', 'created_by', 'modified_by')


class PaymentTermForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(PaymentTermForm, self).__init__(*args, **kwargs)

        self.helper = FormHelper()
        self.helper.form_id = "payment_term-form-id"
        self.helper.form_class = "payment_term-form-class"
        self.helper.layout = Layout(
        HTML("""
            <p><strong style="font-size: 18px;">{}</strong></p>
            <hr>
        """.format(_('Add/Update Payment Term'),)),
        BS5Accordion(
            AccordionGroup(_('PAYMENT TERM DATA'),
                Row(
                    Column('name', css_class='form-group col-md-8 mb-0'),
                    Column('active_status', css_class='form-group col-md-4 mb-0'),
                    css_class='form-row'
                ),
                Row(
                    Column(Field('notes', rows='2'), css_class='form-group col-md-12 mb-0'),
                    css_class='form-row'),
            ),
                HTML('<br>'),
                Submit('save_payment_term', _('Save & Close'), css_class='btn btn-primary fas fa-save'),
                Submit('save_payment_term_new', _('Save & Edit'), css_class='btn btn-primary fas fa-save'),
                Reset('reset', 'Clear', css_class='btn btn-danger'),
                flush=True,
                always_open=True),
        )

    class Meta:
        model = PaymentTerm
        exclude = ('date_created', 'date_modified', 'slug', 'created_by', 'modified_by')


class ReceiptForm(forms.ModelForm):
    costumer = forms.ModelChoiceField(
        queryset=Costumer.objects.filter(is_costumer=1, active_status=1),
        label = _("Please choose Costumer"), initial=1)

    name = forms.CharField(max_length=100, required=False)
    number = forms.IntegerField(required=False)

    def __init__(self, *args, **kwargs):
        super(ReceiptForm, self).__init__(*args, **kwargs)

        self.helper = FormHelper()
        self.helper.form_id = "receipt-form-id"
        self.helper.form_class = "receipt-form-class"
        self.helper.layout = Layout(
        HTML("""
            <p><strong style="font-size: 18px;">{}</strong></p>
            <hr>
        """.format(_('Add/Update Receipt'),)),
        BS5Accordion(
            AccordionGroup(_('RECEIPT DATA'),
                Row(
                    Column('costumer', css_class='form-group col-md-6 mb-0'),
                    css_class='form-row'
                ),),
                HTML('<br>'),
                Submit('save_receipt', _('Next'), css_class='btn btn-primary fas fa-save'),
                Reset('reset', 'Clear', css_class='btn btn-danger'),
                flush=True,
                always_open=True),
        )

    class Meta:
        model = Receipt
        exclude = ('date_created', 'date_modified', 'slug', 'created_by', 'modified_by')


    def clean(self):
        cleaned_data = super().clean()

        costumer = cleaned_data.get('costumer')
        
        if costumer is None or costumer == "":
            self.errors['costumer'] = self.error_class(_("""
            Please choose Costumer or create Invoices First."""))

class DocumentForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        super(DocumentForm, self).__init__(*args, **kwargs)

        self.helper = FormHelper()
        self.helper.form_id = "document-form-id"
        self.helper.form_class = "document-form-class"
        self.helper.layout = Layout(
        HTML("""
            <p><strong style="font-size: 18px;">{}</strong></p>
            <hr>
        """.format(_('Add/Update Document'),)),
        BS5Accordion(
            AccordionGroup(_('DOCUMENT DATA'),
                Row(
                    Column('name', css_class='form-group col-md-9 mb-0'),
                    Column('short_name', css_class='form-group col-md-3 mb-0'),
                ),
                Row(
                Column('active_status', css_class='form-group col-md-3 mb-0'),
                Column('modify_stock', css_class='form-group col-md-3 mb-0'),
                Column('track_payment', css_class='form-group col-md-3 mb-0'),
                Column('track_due_date', css_class='form-group col-md-3 mb-0'),
                ),
                Row(
                    Column(
                    Field('template', rows='2'), css_class='form-group col-md-12 mb-0'),
                ),
                Row(
                    Column(
                    Field('notes', rows='2'), css_class='form-group col-md-12 mb-0'),
                ),
                HTML('<br>'),
                Submit('save_document', _('Save & Close'), css_class='btn btn-primary fas fa-save'),
                Submit('save_document_new', _('Save & New'), css_class='btn btn-primary fas fa-save'),
                Reset('reset', 'Clear', css_class='btn btn-danger'),
                flush=True,
                always_open=True),
        ))

    class Meta:
        model = Document
        exclude = ('date_created', 'date_modified', 'slug', 'created_by', 'modified_by')


class InvoicingForm(forms.ModelForm):
    name = forms.CharField(required=False, max_length=50)
    paid_status = forms.IntegerField(required=False, initial=0)
    delivered_status = forms.IntegerField(initial=0, required=False)
    finished_status = forms.IntegerField(initial=0, required=False)
    active_status = forms.IntegerField(initial=1, required=False)
    number = forms.IntegerField(initial=0, required=False)
        
    def __init__(self, *args, **kwargs):
        super(InvoicingForm, self).__init__(*args, **kwargs)
        self.fields['date'].widget = forms.DateTimeInput(attrs={'type':'datetime-local'})
        self.fields['due_date'].widget = forms.DateTimeInput(attrs={'type':'datetime-local'})
        self.helper = FormHelper()
        self.helper.form_id = "invoicing-form-id"
        self.helper.form_class = "invoicing-form-class"
        self.helper.layout = Layout(
        HTML("""
            <p><strong style="font-size: 18px;">{}</strong></p>
            <hr>
        """.format(_('Add/Update Invoicing'),)),
        BS5Accordion(
            AccordionGroup(_('DOCUMENT DATA'),
                Row( FieldWithButtons('costumer', StrictButton('',  css_class="btn fa fa-plus", 
                data_bs_toggle="modal", data_bs_target="#costumer"), css_class='form-group col-md-9 mb-0'),
                FieldWithButtons('document', StrictButton('',  css_class="btn fa fa-plus", 
                data_bs_toggle="modal", data_bs_target="#document"), css_class='form-group col-md-3 mb-0'),),
                Row(
                    Column('date', css_class='form-group col-md-4 mb-0'),
                    Column('due_date', css_class='form-group col-md-4 mb-0'),
                    FieldWithButtons('warehouse', StrictButton('',  css_class="btn fa fa-plus", 
                    data_bs_toggle="modal", data_bs_target="#warehouse"), css_class='form-group col-md-4 mb-0'),
                ),
                Row(
                FieldWithButtons('payment_term', StrictButton('',  css_class="btn fa fa-plus", 
                data_bs_toggle="modal", data_bs_target="#payment_term"), css_class='form-group col-md-3 mb-0'),
                FieldWithButtons('payment_method', StrictButton('',  css_class="btn fa fa-plus", 
                data_bs_toggle="modal", data_bs_target="#payment_method"), css_class='form-group col-md-3 mb-0'),
                FieldWithButtons('bank_account', StrictButton('',  css_class="btn fa fa-plus", 
                data_bs_toggle="modal", data_bs_target="#bank_account"), css_class='form-group col-md-6 mb-0'),
                ),
                Column(
                    Field('notes', rows='2'), css_class='form-group col-md-12 mb-0'),
                Column(Field('public_notes', rows='2'), css_class='form-group col-md-12 mb-0'),),
                HTML('<br>'),
                Submit('save_invoicing', _('Next'), css_class='btn btn-primary fas fa-save'),
                Reset('reset', 'Clear', css_class='btn btn-danger'),
                flush=True,
                always_open=True),
        )

    class Meta:
        model = Invoicing
        exclude = ('date_created', 'date_modified', 'slug', 'created_by', 'modified_by')

    def clean(self):

        cleaned_data = super().clean()

        date = cleaned_data.get('date')
        due_date = cleaned_data.get('due_date')
        
        if due_date <= date:
            self.errors['date'] = self.error_class(_("""Due date must be greater than Invoicing date
            """))


class InvoicingItemForm(forms.ModelForm):
    SERVICE = 'SERVICE'
    PRODUCT = 'PRODUCT'
    
    PRODUCT_CHOICES = ((SERVICE, _('Service')), (PRODUCT, _('Product')))
    type = forms.ChoiceField(choices=PRODUCT_CHOICES, initial=PRODUCT, required=False)

    barcode = forms.CharField(label=_("Product code / Barcode"), max_length=100, required=False, 
    widget=forms.TextInput(attrs={'autofocus': 'autofocus'}))

    tax = forms.ModelChoiceField(queryset=Tax.objects.filter(active_status=1), initial=1, required=False)
    price = forms.DecimalField(max_digits=18, decimal_places=6, initial=0, 
    widget=forms.NumberInput(attrs={'autocomplete': "off"}))
    quantity = forms.DecimalField(max_digits=18, decimal_places=6, initial=0, widget=forms.TextInput)
    discount = forms.DecimalField(max_digits=4, decimal_places=2, initial=0, widget=forms.TextInput)
    invoicing = forms.CharField(required=False, widget=forms.NumberInput)
    product = forms.ModelChoiceField(required=False, queryset=Product.objects.filter(active_status=1),
    widget=forms.Select(attrs={'class': 'product-select'}))

    def __init__(self, *args, **kwargs):
        super(InvoicingItemForm, self).__init__(*args, **kwargs)
        
        self.fields['price'].widget = ListTextWidget(data_list=[], name='price_list')

        self.helper = FormHelper()
        self.helper.form_id = "invoicing-items-form-id"
        self.helper.form_class = "form-inline"
        self.helper.layout = Layout(
        BS5Accordion(
            AccordionGroup(_('INVOICE ITEMS'),
            Row('barcode'),
            Row(
                Column('product', css_class='form-group col-md-4 mb-0'),
                Column('type', css_class='form-group col-md-2 mb-0'),
                Column('price', css_class='form-group col-md-2 mb-0'),
                Column('quantity', css_class='form-group col-md-1 mb-0'),
                Column('discount', css_class='form-group col-md-1 mb-0'),
                Column('tax', css_class='form-group col-md-2 mb-0'),
                css_class='form-row'),
            
                Submit('add_item', _('Add Item'), css_class='btn btn-primary fa fa-plus'),
        ),))
    
    def clean(self):
        cleaned_data = super().clean()
        
        price = cleaned_data.get('price')
        discount = cleaned_data.get('discount')
        product = cleaned_data.get('product')
        
        if product == "":
            self.errors['product'] = self.error_class(_("""
                Product must not be blank."""))

        try:
            pr = Product.objects.get(name=product)
            min_price = pr.min_sell_price

            if price < min_price:
                self.errors['price'] = self.error_class(_("""
                Price is lower than the product Minimum selling price {}.""".format(min_price)))

        except Product.DoesNotExist:
            min_price = 0

        if discount is None:
            self.errors['discount'] = self.error_class(_("""
            discount must be between 0 and 99.99."""))
        elif discount > 100 or discount < 0:
            self.errors['discount'] = self.error_class(_("""
            discount must be between 0 and 100."""))

    def clean_invoicing(self):
        return None

    class Meta:
        model = InvoicingItem
        fields = "__all__"


class ProductReturnItemForm(forms.ModelForm):
    SERVICE = 'SERVICE'
    PRODUCT = 'PRODUCT'
    
    PRODUCT_CHOICES = ((SERVICE, _('Service')), (PRODUCT, _('Product')))
    type = forms.ChoiceField(choices=PRODUCT_CHOICES, initial=PRODUCT, required=False)

    barcode = forms.CharField(label=_("Product code / Barcode"), max_length=100, required=False, 
    widget=forms.TextInput(attrs={'autofocus': 'autofocus'}))

    tax = forms.ModelChoiceField(queryset=Tax.objects.filter(active_status=1), initial=1, required=False)
    price = forms.DecimalField(max_digits=18, decimal_places=6, initial=0, 
    widget=forms.NumberInput(attrs={'autocomplete': "off"}))
    quantity = forms.DecimalField(max_digits=18, decimal_places=6, initial=0, widget=forms.TextInput)
    discount = forms.DecimalField(max_digits=4, decimal_places=2, initial=0, widget=forms.TextInput)
    invoicing = forms.CharField(required=False, widget=forms.NumberInput)
    product = forms.ModelChoiceField(required=False, queryset=Product.objects.filter(active_status=1),
    widget=forms.Select(attrs={'class': 'product-select'}))

    def __init__(self, *args, **kwargs):
        super(ProductReturnItemForm, self).__init__(*args, **kwargs)
        
        self.fields['price'].widget = ListTextWidget(data_list=[], name='price_list')

        self.helper = FormHelper()
        self.helper.form_id = "invoicing-items-form-id"
        self.helper.form_class = "form-inline"
        self.helper.layout = Layout(
        BS5Accordion(
            AccordionGroup(_('INVOICE ITEMS'),
            Row('barcode'),
            Row(
                Column('product', css_class='form-group col-md-4 mb-0'),
                Column('type', css_class='form-group col-md-2 mb-0'),
                Column('price', css_class='form-group col-md-2 mb-0'),
                Column('quantity', css_class='form-group col-md-1 mb-0'),
                Column('discount', css_class='form-group col-md-1 mb-0'),
                Column('tax', css_class='form-group col-md-2 mb-0'),
                css_class='form-row'),
            
                Submit('add_item', _('Add Item'), css_class='btn btn-primary fa fa-plus'),
        ),))
    
    def clean(self):
        cleaned_data = super().clean()
        
        price = cleaned_data.get('price')
        discount = cleaned_data.get('discount')
        product = cleaned_data.get('product')
        
        if product == "":
            self.errors['product'] = self.error_class(_("""
                Product must not be blank."""))

        try:
            pr = Product.objects.get(name=product)
            min_price = pr.min_sell_price

            if price < min_price:
                self.errors['price'] = self.error_class(_("""
                Price is lower than the product Minimum selling price {}.""".format(min_price)))

        except Product.DoesNotExist:
            min_price = 0

        if discount is None:
            self.errors['discount'] = self.error_class(_("""
            discount must be between 0 and 99.99."""))
        elif discount > 100 or discount < 0:
            self.errors['discount'] = self.error_class(_("""
            discount must be between 0 and 100."""))

    def clean_invoicing(self):
        return None

    class Meta:
        model = ProductReturnItem
        fields = "__all__"


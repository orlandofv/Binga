# -*- coding: utf-8 -*-
from decimal import Decimal

from django import forms

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Submit, Row, Column, Reset, HTML
from crispy_forms.bootstrap import FieldWithButtons, StrictButton, AccordionGroup, TabHolder, Tab, Field
from django.utils.translation import ugettext_lazy as _
from crispy_bootstrap5.bootstrap5 import BS5Accordion

from django.utils import timezone
from users.models import User
from .models import (Product, Warehouse, CostumerInvoice, CostumerInvoiceItem, CostumerReceipt,
PaymentTerm, PaymentMethod)

from isis.models import Tax, Costumer
from bank.models import BankAccount

from asset_app.fields import ListTextWidget


class CostumerInvoiceItemForm(forms.ModelForm):
    SERVICE = 'SERVICE'
    PRODUCT = 'PRODUCT'
    
    PRODUCT_CHOICES = ((SERVICE, _('Service')), (PRODUCT, _('Product')))
    type = forms.ChoiceField(choices=PRODUCT_CHOICES, initial=PRODUCT, required=False)

    barcode = forms.CharField(label=_("Product code / Barcode"), max_length=100, required=False, 
    widget=forms.TextInput(attrs={'autofocus': 'autofocus'}))

    tax = forms.ModelChoiceField(queryset=Tax.objects.filter(active_status=1), initial=1, required=False)
    price = forms.DecimalField(required=False, max_digits=18, decimal_places=6, initial=0, 
    widget=forms.NumberInput(attrs={'autocomplete': "off"}))
    quantity = forms.DecimalField(required=False, max_digits=18, decimal_places=6, initial=0, widget=forms.TextInput)
    discount = forms.DecimalField(required=False, max_digits=4, decimal_places=2, initial=0, widget=forms.TextInput)
    invoice = forms.CharField(required=False, widget=forms.NumberInput)
    product = forms.ModelChoiceField(required=False, 
    queryset=Product.objects.filter(active_status=1),
    widget=forms.Select(attrs={'class': 'product-select'}))
    
    total = forms.DecimalField(required=False, max_digits=4, decimal_places=2, initial=0, 
    widget=forms.HiddenInput)

    tax_total = forms.DecimalField(required=False, max_digits=4, decimal_places=2, initial=0, 
    widget=forms.HiddenInput)

    sub_total = forms.DecimalField(required=False, max_digits=4, decimal_places=2, initial=0, 
    widget=forms.HiddenInput)

    discount_total = forms.DecimalField(required=False, max_digits=4, decimal_places=2, initial=0, 
    widget=forms.HiddenInput)

    def __init__(self, *args, **kwargs):
        super(CostumerInvoiceItemForm, self).__init__(*args, **kwargs)
        
        self.fields['price'].widget = ListTextWidget(data_list=[], name='price_list')

        self.helper = FormHelper()
        self.helper.form_id = "invoice-items-form-id"
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
        
        try:
            pr = Product.objects.get(name=product)
            min_price = pr.min_sell_price

            if price < min_price:
                self.errors['price'] = self.error_class(_("""
                Price is lower than the product Minimum selling price {}.""".format(min_price)))

        except Product.DoesNotExist:
            min_price = 0

        if discount is not None:
            if Decimal(discount) > Decimal(100) or Decimal(discount) < Decimal(0):
                self.errors['discount'] = self.error_class(_("""
                discount must be between 0 and 100."""))

        return cleaned_data

    def clean_invoice(self):
        return None

    class Meta:
        model = CostumerInvoiceItem
        fields = "__all__"


class CostumerInvoiceForm(forms.ModelForm):
    name = forms.CharField(required=False, max_length=50)
    paid_status = forms.IntegerField(required=False, initial=0)
    delivered_status = forms.IntegerField(initial=0, required=False)
    finished_status = forms.IntegerField(initial=0, required=False)
    active_status = forms.IntegerField(initial=1, required=False)
    number = forms.IntegerField(initial=0, required=False)
        
    def __init__(self, *args, **kwargs):
        super(CostumerInvoiceForm, self).__init__(*args, **kwargs)

        self.helper = FormHelper()
        self.helper.form_id = "invoice-form-id"
        self.helper.form_class = "invoice-form-class"
        self.helper.layout = Layout(
        HTML("""
            <p><strong style="font-size: 18px;">{}</strong></p>
            <hr>
        """.format(_('Add/Update CostumerInvoice'),)),
        BS5Accordion(
            AccordionGroup(_('INVOICE DATA'),
                FieldWithButtons('costumer', StrictButton('',  css_class="btn fa fa-plus", 
                data_bs_toggle="modal", data_bs_target="#costumer"), css_class='form-group col-md-12 mb-0'),
                Row(
                    Column('date', css_class='form-group col-md-3 mb-0'),
                    Column('due_date', css_class='form-group col-md-3 mb-0'),
                    FieldWithButtons('warehouse', StrictButton('',  css_class="btn fa fa-plus", 
                    data_bs_toggle="modal", data_bs_target="#warehouse"), css_class='form-group col-md-6 mb-0'),
                ),
                Row(
                FieldWithButtons('payment_term', StrictButton('',  css_class="btn fa fa-plus", 
                data_bs_toggle="modal", data_bs_target="#payment_term"), css_class='form-group col-md-3 mb-0'),
                FieldWithButtons('payment_method', StrictButton('',  css_class="btn fa fa-plus", 
                data_bs_toggle="modal", data_bs_target="#payment_method"), css_class='form-group col-md-3 mb-0'),
                FieldWithButtons('bank_account', StrictButton('',  css_class="btn fa fa-plus", 
                data_bs_toggle="modal", data_bs_target="#bank_account"), css_class='form-group col-md-3 mb-0'),
                ),
                Column(Field('notes', rows='2'), css_class='form-group col-md-12 mb-0'),
                Column(Field('public_notes', rows='2'), css_class='form-group col-md-12 mb-0'),),
                HTML('<br>'),
                Submit('save_invoice', _('Next'), css_class='btn btn-primary fas fa-save'),
                Reset('reset', 'Clear', css_class='btn btn-danger'),
                flush=True,
                always_open=True),
        )

    class Meta:
        model = CostumerInvoice
        exclude = ('date_created', 'date_modified', 'slug', 'created_by', 'modified_by')


class CostumerForm(forms.ModelForm):
    YES = 1
    NO = 0

    COSTUMER_CHOICES = ((NO, _("No")), (YES, _("Yes")))

    name = forms.CharField(label=_('Costumer Name'), 
    widget=forms.TextInput, max_length=100)
    parent = forms.ModelChoiceField(label=_('Parent Costumer'), 
    queryset=Costumer.objects.filter(is_costumer=1), 
    required=False, initial=0)
    is_supplier = forms.ChoiceField(label=_("Is Supplier?"), widget=forms.RadioSelect, 
    choices=COSTUMER_CHOICES, initial=NO)
    email = forms.CharField(max_length = 254, widget=forms.EmailInput, required=False)
    website = forms.URLField(max_length = 254, widget=forms.URLInput, required=False)
    current_credit = forms.DecimalField(max_digits=18, decimal_places=6, required=False, initial=0)
    is_costumer = forms.IntegerField(initial=1, required=False, widget=forms.HiddenInput)

    def __init__(self, *args, **kwargs):
        super(CostumerForm, self).__init__(*args, **kwargs)

        self.helper = FormHelper(self)
        self.helper.form_id = "costumer-form-id"
        self.helper.form_class = "costumer-form-class"
        self.helper.layout = Layout(
                HTML("""
            <p><strong style="font-size: 18px;">{}</strong></p>
            <hr>
        """.format(_('Add/Update Costumer'),)),
            BS5Accordion(
            AccordionGroup(_('Costumer Data'),
            Row(
                Column('name', css_class='form-group col-md-8 mb-0'),
                Column('vat', css_class='form-group col-md-4 mb-0'),
                ),
            Row(
                Column('country', css_class='form-group col-md-3 mb-0'),
                Column('province', css_class='form-group col-md-3 mb-0'),
                Column('city', css_class='form-group col-md-3 mb-0'),
                Column('zip', css_class='form-group col-md-3 mb-0'),
                ),
            Row(
                Column('warehouse', css_class='form-group col-md-3 mb-0'),
                Column('type', css_class='form-group col-md-3 mb-0'),
                Column('capital', css_class='form-group col-md-3 mb-0'),
                Column('active_status', css_class='form-group col-md-3 mb-0'),
                ),
            Row(
                Column('max_credit', css_class='form-group col-md-3 mb-0'),
                Column('parent', css_class='form-group col-md-3 mb-0'),
                Column('is_supplier', css_class='form-group col-md-6 mb-0'),
                
            ),
            Row(Column('address', css_class='form-group col-md-12 mb-0'),),
            Row(Column('contacts', css_class='form-group col-md-12 mb-0'),),
            Row(Column('manager', css_class='form-group col-md-12 mb-0'),),
            Row(
                Column('email', css_class='form-group col-md-6 mb-0'),
                Column('website', css_class='form-group col-md-6 mb-0'),
                ),
            # Row(Column(Field('notes', rows='2'), css_class='form-group col-md-12 mb-0'),),
            Submit('save_costumer', _('Save & Close'), css_class='btn btn-primary fas fa-save'),
            Submit('save_costumer_new', _('Save & New'), css_class='btn btn-primary fas fa-save'),
            Reset('reset', 'Clear', css_class='btn btn-danger'),
            ),
            flush=True,
            always_open=True),
        )
    
    class Meta:
        model = Costumer
        exclude = ('date_created', 'date_modified', 'slug', 'created_by', 'modified_by')

    def clean_parent(self):
        pass


class CostumerReceiptForm(forms.ModelForm):
    costumer = forms.ModelChoiceField(
        queryset=Costumer.objects.filter(is_costumer=1, active_status=1),
        label = _("Please choose Costumer"), initial=1)

    bank_account = forms.ModelChoiceField(queryset=BankAccount.objects.filter(acc_status=1), required=False)

    name = forms.CharField(max_length=100, required=False)
    number = forms.IntegerField(required=False)

    def __init__(self, *args, **kwargs):
        super(CostumerReceiptForm, self).__init__(*args, **kwargs)

        self.helper = FormHelper()
        self.helper.form_id = "costumer_receipt-form-id"
        self.helper.form_class = "costumer_receipt-form-class"
        self.helper.layout = Layout(
        HTML("""
            <p><strong style="font-size: 18px;">{}</strong></p>
            <hr>
        """.format(_('Add/Update CostumerReceipt'),)),
        BS5Accordion(
            AccordionGroup(_('RECEIPT DATA'),
                Row(
                    Column('costumer', css_class='form-group col-md-8 mb-0'),
                    Column('bank_account', css_class='form-group col-md-4 mb-0'),
                    css_class='form-row'
                ),),
                HTML('<br>'),
                Submit('save_costumer_receipt', _('Next'), css_class='btn btn-primary fas fa-save'),
                Reset('reset', 'Clear', css_class='btn btn-danger'),
                flush=True,
                always_open=True),
        )

    class Meta:
        model = CostumerReceipt
        exclude = ('date_created', 'date_modified', 'slug', 'created_by', 'modified_by')


    def clean(self):
        cleaned_data = super().clean()

        costumer = cleaned_data.get('costumer')
        
        if costumer is None or costumer == "":
            self.errors['costumer'] = self.error_class(_("""
            Please choose Costumer or create Invoices First."""))



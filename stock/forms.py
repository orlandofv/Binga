# -*- coding: utf-8 -*-
import datetime 
from datetime import timedelta

from django import forms
from django.utils.translation import ugettext_lazy as _
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Submit, Row, Column, Reset, HTML
from crispy_forms.bootstrap import FieldWithButtons, StrictButton, AccordionGroup, Field
from .models import Stock
from warehouse.models import Warehouse


class StockSearchForm(forms.Form):
    _start_date = datetime.datetime.now() - timedelta(days=30)
    start_date = forms.DateTimeField(label=_("Start date"), 
    widget=forms.DateTimeInput(attrs={'type':'datetime-local'}), 
    initial=datetime.datetime.now() - timedelta(days=30))
    end_date = forms.DateTimeField(label=_("End date"), 
    widget=forms.DateTimeInput(attrs={'type':'datetime-local'}), 
    initial=datetime.datetime.now())
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        self.helper = FormHelper()
        self.helper.form_id = "search-form-id"
        self.helper.form_class = "search-form-class"
        self.helper.layout = Layout(
            Row(Column('start_date', css_class='form-group col-md-4 mb-0'),
            FieldWithButtons('end_date', StrictButton('',  
            css_class="btn fa fa-binoculars", type='Submit'), css_class='form-group col-md-4 mb-0'),))


class WarehouseStockSearchForm(forms.Form):
    _start_date = datetime.datetime.now() - timedelta(days=30)
    start_date = forms.DateTimeField(label=_("Start date"), 
    widget=forms.DateTimeInput(attrs={'type':'datetime-local'}), 
    initial=datetime.datetime.now() - timedelta(days=30))
    end_date = forms.DateTimeField(label=_("End date"), 
    widget=forms.DateTimeInput(attrs={'type':'datetime-local'}), 
    initial=datetime.datetime.now())

    warehouse = forms.ModelChoiceField(label=_("Warehouse"), 
    queryset=Warehouse.objects.filter(active_status=1), required=False)

    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        self.helper = FormHelper()
        self.helper.form_id = "search-form-id"
        self.helper.form_class = "search-form-class"
        self.helper.layout = Layout(
            Row(Column('start_date', css_class='form-group col-md-4 mb-0'),
            FieldWithButtons('end_date', StrictButton('',  
            css_class="btn fa fa-binoculars", type='Submit'), css_class='form-group col-md-4 mb-0'),
            Column('warehouse', css_class='form-group col-md-4 mb-0'),),
            HTML("<hr>"))



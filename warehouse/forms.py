# -*- coding: utf-8 -*-
from django import forms
from .models import (Warehouse)


from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Submit, Row, Column, Reset, HTML, Field
from crispy_forms.bootstrap import FieldWithButtons, StrictButton, AccordionGroup, TabHolder, Tab
from django.utils.translation import ugettext_lazy as _
from crispy_bootstrap5.bootstrap5 import BS5Accordion


class WarehouseForm(forms.ModelForm):

    parent = forms.ModelChoiceField(queryset=Warehouse.objects.all(), required=False)

    def __init__(self, *args, **kwargs):
        super(WarehouseForm, self).__init__(*args, **kwargs)

        self.helper = FormHelper()
        self.helper.form_id = "warehouse-form-id"
        self.helper.form_class = "warehouse-form-class"
        self.helper.layout = Layout(
        HTML("""
            <p><strong style="font-size: 18px;">{}</strong></p>
            <hr>
        """.format(_('Add/Update Warehouse'),)),
        BS5Accordion(
            AccordionGroup(_('WAREHOUSE MAIN DATA'),
                Row(
                    Column('name', css_class='form-group col-md-6 mb-0'),
                    Column('parent', css_class='form-group col-md-6 mb-0'),
                css_class='form-row'),
                Row(
                    Column('address', css_class='form-group col-md-12 mb-0'),
                css_class='form-row'
                ),
                Row(
                    Column('contacts', css_class='form-group col-md-12 mb-0'),
                css_class='form-row'
                ),
                
                Row(
                    Column('active_status', css_class='form-group col-md-6 mb-0'),
                    Column('open_status', css_class='form-group col-md-6 mb-0'),
                css_class='form-row'),
                Row(
                    Column(Field('description', rows='2'), css_class='form-group col-md-12 mb-0'),
                css_class='form-row'),
                
                Row(
                    Column(Field('notes', rows='2'), css_class='form-group col-md-12 mb-0'),
                    css_class='form-row'),
            ),
                HTML('<br>'),
                Submit('save_warehouse', _('Save & Close'), css_class='btn btn-primary fas fa-save'),
                Submit('save_warehouse_new', _('Save & Edit'), css_class='btn btn-primary fas fa-save'),
                Reset('reset', 'Clear', css_class='btn btn-danger'),
                flush=True,
                always_open=True),
        )
    
    def clean_parent(self):
        pass

    class Meta:
        model = Warehouse
        exclude = ('date_created', 'date_modified', 'slug', 'created_by', 'modified_by')


class WarehouseTransferForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        super(WarehouseTransferForm, self).__init__(*args, **kwargs)

        

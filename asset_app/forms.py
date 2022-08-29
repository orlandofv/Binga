# -*- coding: utf-8 -*-
import datetime

from lib2to3.pgen2.token import RIGHTSHIFTEQUAL
from secrets import choice
import sys

from django import forms
from .models import (Component, Maintenance, Costumer, 
Allocation, Group, System, Type, SubType, Vendor, Item, Settings, WorkOrder, Action)
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Submit, Row, Column, Reset, HTML, Button
from crispy_forms.bootstrap import FieldWithButtons, StrictButton, AccordionGroup, Field
from django.utils.translation import ugettext_lazy as _
from crispy_bootstrap5.bootstrap5 import BS5Accordion
from django.utils import timezone

from users.models import User

from .fields import ListTextWidget


class SettingsForm(forms.ModelForm):
    name = forms.CharField(label=_('Company Name'))
    address = forms.CharField(label=_('Address'), required=False, max_length=255)
    cell = forms.CharField(label=_('Cell'), required=False, max_length=255)
    cell_2 = forms.CharField(label=_('Cell 2'), required=False, max_length=255)
    telephone = forms.CharField(label=_('Telephone'), required=False, max_length=255)
    fax = forms.CharField(label=_('Fax'), required=False, max_length=255)
    email = forms.EmailField(label=_('Email'), required=True)
    web = forms.CharField(label=_('Web Site'), max_length=255, required=False)
    logo = forms.ImageField(label=_('Logo'), max_length=255, required=False)
    logo_square = forms.ImageField(label=_('Logo Square'), max_length=255, required=False)
    notes = forms.CharField(label=_('Notes'), required=False, 
    widget=forms.Textarea)

    def __init__(self, *args, **kwargs):
        super(SettingsForm, self).__init__(*args, **kwargs)

        self.helper = FormHelper()
        self.helper.form_id = "settings-form-id"
        self.helper.form_class = "settings-form-class"
        self.helper.layout = Layout(
        HTML("""
            <p><strong style="font-size: 18px;">{}</strong></p>
            <hr>
        """.format(_('Add/Update Settings'),)),
        BS5Accordion(
        AccordionGroup(_('Settings'),
            'name',
            'address',
            Row(
                Column('vat', css_class='form-group col-md-4 mb-0'),
                Column('cell', css_class='form-group col-md-4 mb-0'),
                Column('cell_2', css_class='form-group col-md-4 mb-0'),
                css_class='form-row'),
            Row(
                Column('telephone', css_class='form-group col-md-6 mb-0'),
                Column('fax', css_class='form-group col-md-6 mb-0'),
                css_class='form-row'),
            Row(
                Column('email', css_class='form-group col-md-6 mb-0'),
                Column('web', css_class='form-group col-md-6 mb-0'),
                css_class='form-row'),
            Row(
                Column('logo', css_class='form-group col-md-6 mb-0'),
                Column('logo_square', css_class='form-group col-md-6 mb-0'),
                css_class='form-row'),
            'notes',
            Submit('save_settings', _('Save & Close'), css_class='btn btn-primary fas fa-save'),
            Submit('save_settings_new', _('Save & Edit'), css_class='btn btn-primary fas fa-save'),
            Reset('reset', 'Clear', css_class='btn btn-danger'),
            flush=True,
            always_open=True
            ),))

    class Meta:
        model = Settings
        exclude = ('date_created', 'date_modified', 'slug', 'created_by', 'modified_by')


class ComponentForm(forms.ModelForm):
    """Form definition for Component."""
    
    component_no = forms.IntegerField(widget=forms.NumberInput, label=_('System No.'),)
    name = forms.CharField(widget=forms.TextInput, label=_('Component Name'))
    manufacturer = forms.CharField(label=_('Manufacturer'))
    stock_code = forms.CharField(label=_('Stock Code'))
    maintenance= forms.ModelChoiceField(queryset=Maintenance.objects.all(),
    label=_('Maintenance'))
    notes = forms.CharField(label=_('Notes'), widget=forms.Textarea, required=False)
    
    def __init__(self, *args, **kwargs):
        super(ComponentForm, self).__init__(*args, **kwargs)

        self.helper = FormHelper()
        self.helper.form_id = "component-form-id"
        self.helper.form_class = "component-form-class"
        self.helper.layout = Layout(
             HTML("""
            <p><strong style="font-size: 18px;">{}</strong></p>
            <hr>
        """.format(_('Add/Update Component'),)),
            BS5Accordion(
        AccordionGroup(_('Component Data'),
                Row(
                    Column('component_no', css_class='form-group col-md-6 mb-0'),
                    Column('name', css_class='form-group col-md-6 mb-0'),
                    css_class='form-row'
                ),
                Row(
                    Column('manufacturer', css_class='form-group col-md-6 mb-0'),
                    Column('stock_code', css_class='form-group col-md-6 mb-0'),
                    css_class='form-row'
                ),
                Row(
                    Column("image", css_class='form-group col-md-12 mb-0')
                    ),
            FieldWithButtons('maintenance', StrictButton('',  css_class="btn fa fa-plus",
            data_bs_toggle="modal", data_bs_target="#maintenance")),
            # Row(Column(Field('notes', rows='2'), css_class='form-group col-md-12 mb-0'),),
            Submit('save_component', _('Save & Close'), css_class='btn btn-primary fas fa-save'),
            Submit('save_component_new', _('Save & New'), css_class='btn btn-primary fas fa-save'),
            Reset('reset', 'Clear', css_class='btn btn-danger'),
            flush=True,
            always_open=True),
            
        ))

    class Meta:
        """Meta definition for Componentform."""

        model = Component
        fields = ("component_no", "name","manufacturer", "stock_code",
        "maintenance","image","notes",)


class MaintenanceForm(forms.ModelForm):
    cm = 'Cm'
    kg = 'Kg'
    gb = 'Gb'
    mb = 'Mb'
    piece = 'Piece'
    m3 = 'M3'
    km = 'Km'
    l = 'L'
    g = 'G'

    UNIT_CHOICES = ((cm, _('Cm')), (kg, _('Kg')), (l, _('L')),(gb, _('Gb')), 
    (mb, _('Mb')), (piece, _('Piece')), (m3, _('M³')), (km, _('Km')), (g, _('G')))

    ROUTINE = 'Routine'
    PREVENTIVE = 'Preventive'
    CORRECTIVE = 'Corrective'
    PREDECTIVE = 'Predective'

    MAINTENANCE_CHOICES = (
        (ROUTINE, 'Routine'), 
        (PREVENTIVE, 'Preventive'), 
        (CORRECTIVE, 'Corrective'), 
        (PREDECTIVE, 'Predective'), 
    )

    HOURS = 'Hours'
    DAYS = 'Days'
    MONTHS = 'Months'
    KM = 'KM'

    MAINTENANCE_SCHEDULE = (
        (HOURS, 'Hours'), (DAYS, 'Days'), (MONTHS, 'Months'), 
        (KM, 'KM\'s'), 
    )

    name = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control'}), max_length=50)
    type = forms.ChoiceField(choices=MAINTENANCE_CHOICES)
    schedule = forms.ChoiceField(choices=MAINTENANCE_SCHEDULE)
    frequency = forms.FloatField(widget=forms.NumberInput, initial=1)
    time_allocated = forms.FloatField(widget=forms.NumberInput, initial=1)
    time_schedule = forms.ChoiceField(choices=MAINTENANCE_SCHEDULE)
    notes = forms.CharField(label=_('Notes'), widget=forms.Textarea, required=False)

    action = forms.CharField(label=_('Action'), max_length=255, required=False)
    item = forms.CharField(label=_('Item'), max_length=255, required=False)
    cost = forms.DecimalField(label=_('Cost'), decimal_places=2, max_digits=9, initial=0, required=False) 
    quantity = forms.DecimalField(label=_('Quantity'), decimal_places=2, max_digits=9, initial=0, required=False)
    unit = forms.ChoiceField(choices=UNIT_CHOICES, initial=piece)

    update = forms.CharField(max_length=255, required=False, widget=forms.HiddenInput()) 

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields['item'].widget = ListTextWidget(data_list=Item.objects.all(), name='item')
        self.fields['action'].widget = ListTextWidget(data_list=Action.objects.all(), name='action')

        self.helper = FormHelper(self)
        self.helper.form_show_errors = False
        self.helper.attrs = {"novalidate": ''}
        self.helper.form_id = "maintenance-form-id"
        self.helper.form_class = "maintenance-form-class"
        self.helper.layout = Layout(
                HTML("""
            <p><strong style="font-size: 18px;">{}</strong></p>
            <hr>
        """.format(_('Add/Update Maintenance'),)),
            BS5Accordion(
            AccordionGroup(_('Maintenance Data'),
            Row(Column('name', css_class='form-group col-md-9 mb-0'),
                Column('type', css_class='form-group col-md-3 mb-0'),),
            Row(
                Column('frequency', css_class='form-group col-md-3 mb-0'),
                Column('schedule', css_class='form-group col-md-3 mb-0'),
            ),
            Row(
                Column('time_allocated', css_class='form-group col-md-3 mb-0'),
                Column('time_schedule', css_class='form-group col-md-3 mb-0'),
            ),
            Row(
                FieldWithButtons('action', StrictButton('',  css_class="btn fa fa-minus-circle", id='removeRow'), id='div_id_action'), id='add_action'
            ),

            Button('add_action', _('Add Action'), css_class='btn btn-secondary fas fa-plus'),
            Row(
                # Column(HTML("""<div  class="row"  id="add_item_div">{}</div>""".format(self.item_html)), css_class='form-group col-md-12 mb-0'),
                Column(Field('item', autocomplete='false'), css_class='form-group col-md-6 mb-0'),
                Column('cost', css_class='form-group col-md-2 m-0'),
                Column('quantity', css_class='form-group col-md-2 m-0'), 
                FieldWithButtons('unit', StrictButton('',  css_class="btn fa fa-minus-circle", id='removeItem'), id='div_id_item', css_class='form-group col-md-2 m-0'),
                id='item_row'
            ),
            'update',
            Button('add_item', _('Add Item'), css_class='btn btn-secondary fas fa-plus'),
            HTML('<hr>'),
            Submit('save_maintenance', _('Save & Close'), css_class='btn btn-primary fas fa-save'),
            # Submit('save_maintenance_clone', _('Save and Clone'), css_class='btn btn-secondary fas fa-save'),
            Submit('save_maintenance_new', _('Save & New'), css_class='btn btn-primary fas fa-save'),
            Reset('reset', 'Clear', css_class='btn btn-danger'),

            flush=True,
            always_open=True)
            ),
           
        )

    def clean(self):
        cleaned_data = super().clean()

        print(cleaned_data)

        # Used to check wether is update or not
        update = cleaned_data.get('update')

        frequency = cleaned_data.get('frequency')
        
        name = cleaned_data.get('name')
        action = cleaned_data.get('action')
        time_allocated = cleaned_data.get('time_allocated')

        item = cleaned_data.get('item')
        quantity = cleaned_data.get('quantity')
        cost = cleaned_data.get('cost')
        
        if frequency in (None, ""):
            self.errors['frequency'] = self.error_class([_('Maintenance frequency must not be ' 
            'empty.')])
        elif frequency <= 0:
            self.errors['frequency'] = self.error_class([_('Maintenance frequency must be ' 
            'greater than zero.')])

        if time_allocated in (None, ""):
            self.errors['time_allocated'] = self.error_class([_('Maintenance Time allocated must not be ' 
            'empty.')])

        elif time_allocated <= 0:
             self.errors['time_allocated'] = self.error_class([_('Maintenance Time allocated must be ' 
            'greater than zero.')])

        if name in (None, ""):
             self.errors['name'] = self.error_class([_('Maintenance name must no be ' 
            'empty.')])

        if update == "":
            if action in (None, ""):
                self.errors['action'] = self.error_class([_('Please add at least one action.')])
            
            if item in (None, "") or cost in (None, "") or quantity in (None, "") :
                self.errors['item'] = self.error_class([_('Please add at least one item, cost and its quantity.')])

            if cost <= 0:
                self.errors['cost'] = self.error_class([_('Cost of Item must be greater than zero.')])
            
            if quantity <= 0:
                self.errors['quantity'] = self.error_class([_('Quantity of Item must be greater than zero.')])
        
        return cleaned_data

    class Meta:
        model = Maintenance
        exclude = ('date_created', 'date_modified', 'slug', 'created_by', 'modified_by')


class MaintenanceFormModal(forms.ModelForm):
    ROUTINE = 1
    PREVENTIVE = 2
    CORRECTIVE = 3
    PREDECTIVE = 4

    MAINTENANCE_CHOICES = (
        (ROUTINE, 'Routine'), 
        (PREVENTIVE, 'Preventive'), 
        (CORRECTIVE, 'Corrective'), 
        (PREDECTIVE, 'Predective'), 
    )

    HOURS = 1
    DAYS = 2
    MONTHS = 3
    KM = 4

    MAINTENANCE_SCHEDULE = (
        (HOURS, 'Hours'), (DAYS, 'Days'), (MONTHS, 'Months'), 
        (KM, 'KM\'s'), 
    )
    name = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control'}), max_length=50)
    type = forms.ChoiceField(choices=MAINTENANCE_CHOICES)
    schedule = forms.ChoiceField(choices=MAINTENANCE_SCHEDULE)
    frequency = forms.IntegerField(widget=forms.NumberInput, initial=1)
    time_allocated = forms.FloatField(widget=forms.NumberInput, initial=1)
    action = forms.CharField(widget=forms.TextInput, max_length=255)
    notes = forms.CharField(label=_('Notes'), widget=forms.Textarea, required=False)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.helper = FormHelper(self)
        self.helper.form_show_errors = False
        self.helper.attrs = {"novalidate": ''}
        self.helper.form_id = "maintenance-form-id"
        self.helper.form_class = "maintenance-form-class"
        self.helper.layout = Layout(
                HTML("""
            <p><strong style="font-size: 18px;">{}</strong></p>
            <hr>
        """.format(_('Add/Update Maintenance'),)),
            BS5Accordion(
            AccordionGroup(_('Maintenance Data'),
            Row(Column('name', css_class='form-group col-md-12 mb-0'),),
            Row(
                Column('schedule', css_class='form-group col-md-6 mb-0'),
                Column('frequency', css_class='form-group col-md-6 mb-0'),),
            Row(    
                Column('type', css_class='form-group col-md-6 mb-0'),
                Column('time_allocated', css_class='form-group col-md-6 mb-0'),
            ),
            Row(
                Column('action', css_class='form-group col-md-12 mb-0'),),
            # Row(Column(Field('notes', rows='2'), css_class='form-group col-md-12 mb-0')),
            Submit('save_maintenance_modal', _('Save'), css_class='btn btn-primary fas fa-save'),
            Reset('reset', 'Clear', css_class='btn btn-danger'),
            flush=True,
            always_open=True)
            ),
        )

    def clean(self):
        cleaned_data = super().clean()
        frequency = cleaned_data.get('frequency')

        name = cleaned_data.get('name')
        action = cleaned_data.get('action')
        time_allocated = cleaned_data.get('time_allocated')
       
        if frequency in (None, ""):
            self.errors['frequency'] = self.error_class([_('Maintenance frequency must not be ' 
            'empty.')])
        elif frequency <= 0:
            self.errors['frequency'] = self.error_class([_('Maintenance frequency must be ' 
            'greater than zero.')])

        if time_allocated in (None, ""):
            self.errors['time_allocated'] = self.error_class([_('Maintenance Time allocated must not be ' 
            'empty.')])

        elif time_allocated <= 0:
             self.errors['time_allocated'] = self.error_class([_('Maintenance Time allocated must be ' 
            'greater than zero.')])

        if name in (None, ""):
             self.errors['name'] = self.error_class([_('Maintenance name must no be ' 
            'empty.')])

        if action in (None, ""):
             self.errors['action'] = self.error_class([_('Maintenance Action must no be ' 
            'empty.')])

        return cleaned_data

    class Meta:
        model = Maintenance
        exclude = ('date_created', 'date_modified', 'slug', 'created_by', 'modified_by')


class CostumerForm(forms.ModelForm):
    YES = 1
    NO = 0

    COSTUMER_CHOICES = ((NO, _("No")), (YES, _("Yes")))

    name = forms.CharField(label=_('Costumer Name'), 
    widget=forms.TextInput, max_length=100)
    parent = forms.ModelChoiceField(label=_('Parent Costumer'), queryset=Costumer.objects.all(), 
    required=False, initial=0)
    is_supplier = forms.ChoiceField(label="Is Supplier?", widget=forms.RadioSelect, 
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
                Column('phone', css_class='form-group col-md-4 mb-0'),
                Column('fax', css_class='form-group col-md-4 mb-0'),
                Column('mobile', css_class='form-group col-md-4 mb-0'),
                
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
    

class GroupForm(forms.ModelForm):
    name = forms.CharField(label=_('Group Name'), 
    widget=forms.TextInput, max_length=100)
    notes = forms.CharField(label=_('Notes'), widget=forms.Textarea, required=False)

    def __init__(self, *args, **kwargs):
        super(GroupForm, self).__init__(*args, **kwargs)

        self.helper = FormHelper(self)
        self.helper.form_id = "group-form-id"
        self.helper.form_class = "group-form-class"
        self.helper.layout = Layout(
                HTML("""
            <p><strong style="font-size: 18px;">{}</strong></p>
            <hr>
        """.format(_('Add/Update Group'),)),
            BS5Accordion(
            AccordionGroup(_('Group Data'),
            Row(Column('name', css_class='form-group col-md-12 mb-0'),),
            # Row(Column(Field('notes', rows='2'), css_class='form-group col-md-12 mb-0'),),
            Submit('save_group', _('Save & Close'), css_class='btn btn-primary fas fa-save'),
            Submit('save_group_new', _('Save & New'), css_class='btn btn-primary fas fa-save'),
            Reset('reset', 'Clear', css_class='btn btn-danger'),
            ),
             flush=True,
            always_open=True),
        )
    
    class Meta:
        model = Group
        exclude = ('date_created', 'date_modified', 'slug', 'created_by', 'modified_by')


class SystemForm(forms.ModelForm):
    name = forms.CharField(label=_('System Name'), 
    widget=forms.TextInput, max_length=100)
    group = forms.ModelChoiceField(queryset=Group.objects.all(), label=_('Group Name')) 
    notes = forms.CharField(label=_('Notes'), widget=forms.Textarea, required=False)
	

    def __init__(self, *args, **kwargs):
        super(SystemForm, self).__init__(*args, **kwargs)

        self.helper = FormHelper(self)
        self.helper.form_id = "system-form-id"
        self.helper.form_class = "system-form-class"
        self.helper.layout = Layout(
                HTML("""
            <p><strong style="font-size: 18px;">{}</strong></p>
            <hr>
        """.format(_('Add/Update System'),)),
            BS5Accordion(
            AccordionGroup(_('System Data'),
            Row(Column('name', css_class='form-group col-md-12 mb-0'),),
            FieldWithButtons('group', StrictButton('',  css_class="btn fa fa-plus",
            data_bs_toggle="modal", data_bs_target="#group")),
            # Row(Column(Field('notes', rows='2'), css_class='form-group col-md-12 mb-0'),),
            Submit('save_system', _('Save & Close'), css_class='btn btn-primary fas fa-save'),
            Submit('save_system_new', _('Save & New'), css_class='btn btn-primary fas fa-save'),
            Reset('reset', 'Clear', css_class='btn btn-danger'),
            ),
             flush=True,
            always_open=True),
        )
    
    class Meta:
        model = System
        exclude = ('date_created', 'date_modified', 'slug', 'created_by', 'modified_by')


class TypeForm(forms.ModelForm):
    name = forms.CharField(label=_('Type Name'), 
    widget=forms.TextInput, max_length=100)
    system = forms.ModelChoiceField(queryset=System.objects.all(), label=_('System Name')) 
    notes = forms.CharField(label=_('Notes'), widget=forms.Textarea, required=False)
	

    def __init__(self, *args, **kwargs):
        super(TypeForm, self).__init__(*args, **kwargs)

        self.helper = FormHelper(self)
        self.helper.form_id = "type-form-id"
        self.helper.form_class = "type-form-class"
        self.helper.layout = Layout(
                HTML("""
            <p><strong style="font-size: 18px;">{}</strong></p>
            <hr>
        """.format(_('Add/Update Type'),)),
            BS5Accordion(
            AccordionGroup(_('Type Data'),
            Row(Column('name', css_class='form-group col-md-12 mb-0'),),
            FieldWithButtons('system', StrictButton('',  css_class="btn fa fa-plus",
            data_bs_toggle="modal", data_bs_target="#system")),
            # Row(Column(Field('notes', rows='2'), css_class='form-group col-md-12 mb-0'),),
            Submit('save_type', _('Save & Close'), css_class='btn btn-primary fas fa-save'),
            Submit('save_type_new', _('Save & New'), css_class='btn btn-primary fas fa-save'),
            Reset('reset', 'Clear', css_class='btn btn-danger'),
            ),
             flush=True,
            always_open=True),
           
        )
    
    class Meta:
        model = Type
        exclude = ('date_created', 'date_modified', 'slug', 'created_by', 'modified_by')


class SubTypeForm(forms.ModelForm):
    name = forms.CharField(label=_('SubType Name'), 
    widget=forms.TextInput, max_length=100)
    type = forms.ModelChoiceField(queryset=Type.objects.all(), label=_('Type Name')) 
    notes = forms.CharField(label=_('Notes'), widget=forms.Textarea, required=False)
	

    def __init__(self, *args, **kwargs):
        super(SubTypeForm, self).__init__(*args, **kwargs)

        self.helper = FormHelper(self)
        self.helper.form_id = "subtype-form-id"
        self.helper.form_class = "subtype-form-class"
        self.helper.layout = Layout(
                HTML("""
            <p><strong style="font-size: 18px;">{}</strong></p>
            <hr>
        """.format(_('Add/Update SubType'),)),
            BS5Accordion(
            AccordionGroup(_('SubType Data'),
            Row(Column('name', css_class='form-group col-md-12 mb-0'),),
            FieldWithButtons('type', StrictButton('',  css_class="btn fa fa-plus",
            data_bs_toggle="modal", data_bs_target="#type")),
            # Row(Column(Field('notes', rows='2'), css_class='form-group col-md-12 mb-0'),),
            Submit('save_subtype', _('Save & Close'), css_class='btn btn-primary fas fa-save'),
            Submit('save_subtype_new', _('Save & New'), css_class='btn btn-primary fas fa-save'),
            Reset('reset', 'Clear', css_class='btn btn-danger'),
            ),
             flush=True,
            always_open=True),
           
        )
    
    class Meta:
        model = SubType
        exclude = ('date_created', 'date_modified', 'slug', 'created_by', 'modified_by')


class AllocationForm(forms.ModelForm):
    
    allocation_no = forms.IntegerField(label=('System No.'), widget=forms.NumberInput())
    component = forms.ModelChoiceField(queryset=Component.objects.all(), 
    label=_('Component Name'))
    vendor = forms.ModelChoiceField(queryset=Vendor.objects.all(), label=_('Vendor Name'))
    costumer = forms.ModelChoiceField(queryset=Costumer.objects.all(), label=_('Costumer Name'))
    serial_number = forms.CharField(label=_('Component Serial No.'), max_length=50)
    image = forms.ImageField(label=_('Image'), initial="default.jpg", required=False)
    purchase_amount = forms.DecimalField(widget=forms.NumberInput, initial=0, max_digits=9, 
    decimal_places=2, label=_('Purchase Amount'))
    date_purchased = forms.DateTimeField(widget=forms.DateTimeInput, initial=timezone.now, 
    label=_('Date Purchased'))
    date_allocated = forms.DateTimeField(widget=forms.DateTimeInput, initial=timezone.now, label=_('Date Allocated'))
    depreciation = forms.FloatField(label=_('Depreciation %'), initial=0)
    start_value_hours = forms.FloatField(label=_('Start Value (Hours)'), initial=0)
    start_value_years = forms.FloatField(label=_('Years'), initial=0)
    start_value_milliege = forms.FloatField(label=_('KM'), initial=0)
    garrantee_value_hours = forms.FloatField(label=_('Warrantee Value (Hours)'), initial=0)
    garrantee_value_years = forms.FloatField(label=_('Years'), initial=0)
    garrantee_milliege = forms.FloatField(label=_('KM'), initial=0)
    end_of_life_hours = forms.FloatField(label=_('End of Life (Hours)'), initial=0)
    end_of_life_years = forms.FloatField(label=_('Years'),initial=0)
    end_of_life_milliege = forms.FloatField(label=_('KM'),initial=0)
    warn_before_hours = forms.FloatField(label=_('Warn Before (Hours)'), initial=0)
    warn_before_years = forms.FloatField(label=_('Years'), initial=0)
    warn_before_milliege = forms.FloatField(label=_('KM'), initial=0)
    group = forms.ModelChoiceField(queryset=Group.objects.all(), label=_('Group'))
    system = forms.ModelChoiceField(queryset=System.objects.all(), label=_('System'))
    type = forms.ModelChoiceField(queryset=Type.objects.all(), label=_('Type'))
    subtype = forms.ModelChoiceField(queryset=SubType.objects.all(), label=_('SubType'))
    notes = forms.CharField(label=_('Notes'), widget=forms.Textarea, required=False)
	

    def __init__(self, *args, **kwargs):
        super(AllocationForm, self).__init__(*args, **kwargs)

        self.helper = FormHelper(self)
        self.helper.form_id = "allocation-form-id"
        self.helper.form_class = "allocation-form-class"
        self.helper.layout = Layout(
                HTML("""
            <p><strong style="font-size: 18px;">{}</strong></p>
            <hr>
        """.format(_('Add/Update Allocation'),)),
            BS5Accordion(
            AccordionGroup(_('ALLOCATE COMPONENT'),
                Row(
                Column('allocation_no', css_class='form-group col-md-6 mb-0'),
                Column(FieldWithButtons('component', StrictButton('',  css_class="btn fa fa-plus",
                data_bs_toggle="modal", data_bs_target="#component")), css_class='form-group col-md-6 mb-0')),

                Row(
                    FieldWithButtons('vendor', StrictButton('',  css_class="btn fa fa-plus",
                    data_bs_toggle="modal", data_bs_target="#vendor"), 
                    css_class='form-group col-md-6 mb-0'),
                    Column('serial_number', css_class='form-group col-md-6 mb-0'),
                ),
                Row(Column('image', css_class='form-group col-md-12 mb-0'),),
                Row(
                    Column('date_purchased', css_class='form-group col-md-4 mb-0'),
                    Column('purchase_amount', css_class='form-group col-md-4 mb-0'),
                    Column('date_allocated', css_class='form-group col-md-4 mb-0'),
                ),
                Row(
                    Column('start_value_hours', css_class='form-group col-md-4 mb-0'),
                    Column('start_value_years', css_class='form-group col-md-4 mb-0'),
                    Column('start_value_milliege', css_class='form-group col-md-4 mb-0'),
                ),
                Row(
                    Column('garrantee_value_hours', css_class='form-group col-md-4 mb-0'),
                    Column('garrantee_value_years', css_class='form-group col-md-4 mb-0'),
                    Column('garrantee_milliege', css_class='form-group col-md-4 mb-0'),
                ),
                Row(
                    Column('end_of_life_hours', css_class='form-group col-md-4 mb-0'),
                    Column('end_of_life_years', css_class='form-group col-md-4 mb-0'),
                    Column('end_of_life_milliege', css_class='form-group col-md-4 mb-0'),
                ),
                Row(
                    Column('warn_before_hours', css_class='form-group col-md-4 mb-0'),
                    Column('warn_before_years', css_class='form-group col-md-4 mb-0'),
                    Column('warn_before_milliege', css_class='form-group col-md-4 mb-0'),
                ),
                Row(
                    Column('depreciation', css_class='form-group col-md-4 mb-0'),
                    Column('status', css_class='form-group col-md-4 mb-0'),),
            ),
            AccordionGroup(_('ATTACH TO SYSTEM'),
                Row(
                        FieldWithButtons('group', StrictButton('',  css_class="btn fa fa-plus",
                        data_bs_toggle="modal", data_bs_target="#group"), css_class='form-group col-md-6 mb-0'),
                        FieldWithButtons('system', StrictButton('',  css_class="btn fa fa-plus",
                        data_bs_toggle="modal", data_bs_target="#system"), css_class='form-group col-md-6 mb-0'),
                    ),
                Row(
                        FieldWithButtons('type', StrictButton('',  css_class="btn fa fa-plus",
                        data_bs_toggle="modal", data_bs_target="#type"), css_class='form-group col-md-6 mb-0'),
                        FieldWithButtons('subtype', StrictButton('',  css_class="btn fa fa-plus",
                        data_bs_toggle="modal", data_bs_target="#subtype"), css_class='form-group col-md-6 mb-0'),

                    ),
            ),
            AccordionGroup(_('ATTACH TO LOCATION'),
                Row(
                        FieldWithButtons('costumer', StrictButton('',  css_class="btn fa fa-plus",
                        data_bs_toggle="modal", data_bs_target="#costumer"), css_class='form-group col-md-12 mb-0'), 
            ),),
            # Row(Column(Field('notes', rows='2'), css_class='form-group col-md-12 mb-0'),),
            Submit('save_allocation', _('Save & Close'), css_class='btn btn-primary fas fa-save'),
            Submit('save_allocation_new', _('Save & New'), css_class='btn btn-primary fas fa-save'),
            Reset('reset', 'Clear', css_class='btn btn-danger'),
            flush=True,
            always_open=True),  
        )

    def clean(self):
        cleaned_data = super().clean()
        allocation_no = cleaned_data.get('allocation_no') 
        component = cleaned_data.get('component') 
        vendor = cleaned_data.get('vendor')   
        costumer = cleaned_data.get('costumer') 
        serial_number = cleaned_data.get('serial_number')  
        purchase_amount = cleaned_data.get('purchase_amount')
        date_purchased = cleaned_data.get('date_purchased')
        date_allocated = cleaned_data.get('date_allocated')
        depreciation = cleaned_data.get('depreciation')
        start_value_hours = cleaned_data.get('start_value_hours')
        start_value_years = cleaned_data.get('start_value_years')
        start_value_milliege = cleaned_data.get('start_value_milliege')
        garrantee_value_hours = cleaned_data.get('garrantee_value_hours')
        garrantee_value_years = cleaned_data.get('garrantee_value_years')
        garrantee_milliege = cleaned_data.get('garrantee_milliege')
        end_of_life_hours = cleaned_data.get('end_of_life_hours')
        end_of_life_years = cleaned_data.get('end_of_life_years')
        end_of_life_milliege = cleaned_data.get('end_of_life_milliege')
        warn_before_hours = cleaned_data.get('warn_before_hours')
        warn_before_years = cleaned_data.get('warn_before_years')
        warn_before_milliege = cleaned_data.get('warn_before_milliege')
        group = cleaned_data.get('group')
        system = cleaned_data.get('system')
        type = cleaned_data.get('type')
        subtype = cleaned_data.get('subtype')

        if allocation_no is None:
            self.errors['allocation_no'] = self.error_class(_("""Invalid Allocation Number.
            \nAllocation Number must be from 1 to 4294967295."""))
        else:
            if allocation_no == "" or int(allocation_no) == 0  or int(allocation_no) > 4294967295:
                self.errors['allocation_no'] = self.error_class(_("""Invalid Allocation Number.
                \nAllocation Number must be from 1 to 4294967295."""))

        if component == "":
            self.errors['component'] = self.error_class(_("""Invalid Component.
            \nPlease choose Componet from the Dropdown."""))
        
        if vendor == "":
            self.errors['component'] = self.error_class(_("""Invalid Vendor.
            \nPlease choose Vendor from the Dropdown."""))
        
        if costumer == "":
            self.errors['costumer'] = self.error_class(_("""Invalid Costumer.
            \nPlease choose Costumer from the Dropdown."""))
            
        if group == "":
            self.errors['group'] = self.error_class(_("""Invalid Group.
            \nPlease choose Group from the Dropdown."""))
        
        if system == "":
            self.errors['system'] = self.error_class(_("""Invalid System.
            \nPlease choose System from the Dropdown."""))
        
        if type == "":
            self.errors['type'] = self.error_class(_("""Invalid Type.
            \nPlease choose Type from the Dropdown."""))
        
        if subtype == "":
            self.errors['subtype'] = self.error_class(_("""Invalid SubType.
            \nPlease choose SubType from the Dropdown."""))
        if depreciation is None:
            self.errors['depreciation'] = self.error_class(_("""Invalid Depreciation Value.
            Depreciation value must be from 0 to 100."""))
        else:
            if depreciation == "" or depreciation < 0 or depreciation > 100:
                self.errors['depreciation'] = self.error_class(_("""Invalid Depreciation Value.
                Depreciation value must be from 0 to 100."""))

        if serial_number == "":
            self.errors['serial_number'] = self.error_class(_("""Invalid Serial Number.
            Serial Number must not be empty"""))

        if start_value_hours == 0 and start_value_years == 0 and \
            start_value_milliege ==0:
            self.errors['start_values'] = self.error_class(_("""Invalid Start Values.
            At least one field of Start Values must be greater than zero."""))

        if garrantee_value_hours == 0 and garrantee_value_years ==0 \
            and garrantee_milliege == 0:
            self.errors['garrantee_values'] = self.error_class(_("""Invalid Garrantee Values.
            At least one field of Garrantee Values must be greater than zero."""))

        if end_of_life_hours == 0 and end_of_life_years == 0 \
            and end_of_life_milliege == 0:
            self.errors['end_of_life_values'] = self.error_class(_("""Invalid End of life Values.
            At least one field of End of life Values must be greater than zero."""))

        if warn_before_hours == 0 and warn_before_years == 0 \
            and warn_before_milliege == 0:
            self.errors['warning_values'] = self.error_class(_("""Invalid Warning Values.
            At least one field of Warning Values must be greater than zero."""))
        
    class Meta:
        model = Allocation
        exclude = ('date_created', 'date_modified', 'slug', 'created_by', 'modified_by')


class WorkOrderForm(forms.ModelForm):
    order = forms.IntegerField(label=_('Order Number'))
    responsible = forms.ModelChoiceField(queryset=User.objects.all(), label=_('Person in Charge'))
    start = forms.DateTimeField(label=_("Start date"), initial=timezone.now, 
    widget=forms.DateTimeInput(attrs={'type':'datetime-local'}))
    end = forms.DateTimeField(label=_("End date"), initial=datetime.datetime.now() + datetime.timedelta(days=30), 
    widget=(forms.DateTimeInput(attrs={'type':'datetime-local'})))
    warn_after = forms.DateTimeField(label=_('Warn After'), initial=datetime.datetime.now() + datetime.timedelta(days=15), 
    widget=(forms.DateTimeInput(attrs={'type':'datetime-local'}))) 
    progress = forms.DecimalField(label=_('Work Progress (%)'), max_digits=5, decimal_places=2, 
    initial=0, required=False)
    component = forms.ModelMultipleChoiceField(queryset=Component.objects.filter(active_status=1))

    def __init__(self, *args, **kwargs):
        super(WorkOrderForm, self).__init__(*args, **kwargs)

        self.helper = FormHelper(self)
        self.helper.form_id = "work-form-id"
        self.helper.form_class = "work-form-class"
        self.helper.layout = Layout(
                HTML("""
            <p><strong style="font-size: 18px;">{}</strong></p>
            <hr>
        """.format(_('Add/Update Work Order'),)),
            BS5Accordion(
            AccordionGroup(_('Work Order Data'),
            Row(
                Column('order', css_class='form-group col-md-6 mb-0'),
                Column('responsible', css_class='form-group col-md-4 mb-0'),
                Column('priority', css_class='form-group col-md-2 mb-0'),),
            Row(
                Column('active_status', css_class='form-group col-md-2 mb-0'),
                Column('component', css_class='form-group col-md-10 mb-0'),
                ),
            Row(
                Column('start', css_class='form-group col-md-4 mb-0'),
                Column('end', css_class='form-group col-md-4 mb-0'),
                Column(Field('warn_after', css_class='form-group col-md-4 mb-0'),),),
            HTML("<hr>"),
            Submit('save_workorder', _('Save & Close'), css_class='btn btn-primary fas fa-save'),
            Submit('save_workorder_new', _('Save & New'), css_class='btn btn-primary fas fa-save'),
            Reset('reset', 'Clear', css_class='btn btn-danger'),
            ),
            flush=True,
            always_open=True),)

    class Meta:
        model = WorkOrder
        exclude = ('date_created', 'date_modified', 'slug', 'created_by', 'modified_by')


    def clean(self):
        cleaned_data = super().clean()
        
        order = cleaned_data.get('order')
        responsible = cleaned_data.get('responsible')
        start = cleaned_data.get('start')
        end = cleaned_data.get('end')
        warn_after = cleaned_data.get('warn_after') 
        status = cleaned_data.get('status')
        progress = cleaned_data.get('progress')

        if order == "" or int(order) == 0 or order > 4294967295:
            self.errors['order'] = self.error_class(_("""Invalid Order.
            \nOrder Number must be from 1 to 4294967295."""))

        if responsible == "":
            self.errors['responsible'] = self.error_class(_("""Invalid Person in Charge.
            \nPlease choose Person in Charge of the Work."""))
        
        if start >= end:
            self.errors['start'] = self.error_class(_("""Invalid Start Date.
            \nEnd date must be greater than Start date."""))
        
        if warn_after >= end or warn_after <= start:
            self.errors['warn_after'] = self.error_class(_("""Invalid Warn Date.
            \nChoose Warning date less than End date  and greater than Start date."""))
        
        return cleaned_data
    

class VendorForm(forms.ModelForm):
    name = forms.CharField(label=_('Vendor Name'), 
    widget=forms.TextInput, max_length=100)
    address = forms.CharField(required=False, max_length=255)
    contacts = forms.CharField(required=False, max_length=255)
    manager = forms.CharField(max_length=100, required=False)
    email = forms.EmailField(max_length = 254, required=False)
    notes = forms.CharField(label=_('Notes'), widget=forms.Textarea, required=False)

    def __init__(self, *args, **kwargs):
        super(VendorForm, self).__init__(*args, **kwargs)

        self.helper = FormHelper(self)
        self.helper.form_id = "vendor-form-id"
        self.helper.form_class = "vendor-form-class"
        self.helper.layout = Layout(
                HTML("""
            <p><strong style="font-size: 18px;">{}</strong></p>
            <hr>
        """.format(_('Add/Update Vendor'),)),
            BS5Accordion(
            AccordionGroup(_('Vendor Data'),
            Row(Column('name', css_class='form-group col-md-12 mb-0'),),
            Row(Column('address', css_class='form-group col-md-12 mb-0'),),
            Row(Column('contacts', css_class='form-group col-md-12 mb-0'),),
            Row(Column('manager', css_class='form-group col-md-12 mb-0'),),
            Row(Column('email', css_class='form-group col-md-12 mb-0'),),
            # Row(Column(Field('notes', rows='2'), css_class='form-group col-md-12 mb-0'),),
            Submit('save_vendor', _('Save & Close'), css_class='btn btn-primary fas fa-save'),
            Submit('save_vendor_new', _('Save & New'), css_class='btn btn-primary fas fa-save'),
            Reset('reset', 'Clear', css_class='btn btn-danger'),
            ),
             flush=True,
            always_open=True),
        )
    
    class Meta:
        model = Vendor
        exclude = ('date_created', 'date_modified', 'slug', 'created_by', 'modified_by')

class ItemForm(forms.ModelForm):

    name = forms.CharField(label=_('Item Name'))
    quantity = forms.DecimalField(decimal_places=2, max_digits=9,  initial=1)
    cost = forms.DecimalField(decimal_places=2, max_digits=9,  initial=0)
    notes = forms.CharField(label=_('Notes'), widget=forms.Textarea, required=False)

    def __init__(self, *args, **kwargs):
        super(ItemForm, self).__init__(*args, **kwargs)

        self.fields['name'].widget = ListTextWidget(data_list=Item.objects.all(), name='name')

        self.helper = FormHelper(self)
        self.helper.form_id = "item-form-id"
        self.helper.form_class = "item-form-class"
        self.helper.layout = Layout(
            BS5Accordion(
            AccordionGroup(_('Item Data'),
            Row(Column('name', css_class='form-group col-md-6 mb-0'),
            Column('quantity', css_class='form-group col-md-2 mb-0'),
            Column('cost', css_class='form-group col-md-2 mb-0'),
            Column('unit', css_class='form-group col-md-2 mb-0')),
            Submit('save_item', _('Add'), css_class='btn btn-primary fas fa-save'),
            Reset('reset', 'Clear', css_class='btn btn-danger'),
            ),
             flush=True,
            always_open=True),
        )
    
    class Meta:
        model = Item
        exclude = ('date_created', 'date_modified', 'slug', 'created_by', 'modified_by')


# 
class ActionForm(forms.ModelForm):

    name = forms.CharField(label=_('Item Name'))
    def __init__(self, *args, **kwargs):
        super(ActionForm, self).__init__(*args, **kwargs)

        self.fields['name'].widget = ListTextWidget(data_list=Item.objects.all(), name='name')

        self.helper = FormHelper(self)
        self.helper.form_id = "action-form-id"
        self.helper.form_class = "action-form-class"
        self.helper.layout = Layout(
            BS5Accordion(
            AccordionGroup(_('Action Data'),
            Row(Column('name', css_class='form-group col-md-12 mb-0')),
            Button('add_action', _('Add Action'), css_class='btn btn-secondary fas fa-save'),
            ),
             flush=True,
            always_open=True),
        )
    
    class Meta:
        model = Action
        exclude = ('date_created', 'date_modified', 'slug', 'created_by', 'modified_by')



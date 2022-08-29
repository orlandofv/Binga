# -*- coding: utf-8 -*-
from django.core.exceptions import ValidationError
from django.utils.translation import ugettext_lazy as _

from django import forms
from .models import User

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Submit, Row, Column, Reset, HTML
from crispy_forms.bootstrap import (FieldWithButtons, StrictButton, AccordionGroup, 
TabHolder, Tab, Div)
from crispy_bootstrap5.bootstrap5 import BS5Accordion

from warehouse.models import Warehouse


class LoginForm(forms.ModelForm):
    email = forms.CharField(widget=forms.TextInput(attrs={'placeholder': 'Email'}))
    password = forms.CharField(widget=forms.PasswordInput())

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            'email',
            'password',
            Submit('submit', _('Sign in')),
        )

    class Meta:
        model = User
        fields=('email', 'password')


class UserForm(forms.ModelForm):
    email = forms.CharField(label='Email', max_length=100, widget=forms.EmailInput(attrs={'placeholder': _('Enter Email')}))
    password = forms.CharField(label='Password', widget=forms.PasswordInput(attrs={'placeholder': _('Enter Password')}))
    confirm_password = forms.CharField(label='Confirm Password', widget=forms.PasswordInput(attrs={'placeholder': _('Confirm Password')}))
    warehouse = forms.ModelChoiceField(label='Warehouse',
    queryset=Warehouse.objects.filter(active_status=1), required=False)
    date_joined = forms.DateTimeField(required=False)
    

    def __init__(self, *args, **kwargs):
        super(UserForm, self).__init__(*args, **kwargs)
        
        self.fields['first_active_date'].widget = forms.DateTimeInput(attrs={'type':'datetime-local'})
        self.fields['last_active_date'].widget = forms.DateTimeInput(attrs={'type':'datetime-local'})
        self.helper = FormHelper()
        self.helper.form_id = "user-form-id"
        self.helper.form_class = "user-form-class"
        self.helper.layout = Layout(
        HTML("""
            <p><strong style="font-size: 18px;">{}</strong></p>
            <hr>
        """.format(_('Add/Update User'),)),
        BS5Accordion(
            AccordionGroup(_('MAIN DATA'),
                Row(
                    Column('username', css_class='form-group col-md-3 mb-0'),
                    Column('email', css_class='form-group col-md-3 mb-0'),
                    css_class='form-row'
                ),
            
                Row(
                    Column('password', css_class='form-group col-md-3 mb-0'),
                    Column('confirm_password', css_class='form-group col-md-3 mb-0'),
                    css_class='form-row'
                ),
                
                Row(
                    Column('warehouse', css_class='form-group col-md-3 mb-0'),
                    Column('first_active_date', css_class='form-group col-md-3 mb-0'),
                    Column('last_active_date', css_class='form-group col-md-3 mb-0'),
                    Column('employee', css_class='form-group col-md-3 mb-0'),
                    css_class='form-row'
                ),
                
                Row(
                    Column('first_name', css_class='form-group col-md-6 mb-0'),
                    Column('last_name', css_class='form-group col-md-3 mb-0'),
                    Column('gender', css_class='form-group col-md-3 mb-0'),
                    css_class='form-row'
                ),
                
                Row(
                    Column('address', css_class='form-group col-md-6 mb-0'),
                    Column('vat', css_class='form-group col-md-3 mb-0'),
                    Column('website', css_class='form-group col-md-3 mb-0'),
                    css_class='form-row'
                ),
                Row(
                    Column('country', css_class='form-group col-md-3 mb-0'),
                    Column('province', css_class='form-group col-md-3 mb-0'),
                    Column('city', css_class='form-group col-md-3 mb-0'),
                    Column('zip', css_class='form-group col-md-3 mb-0'),
                    css_class='form-row'
                ),
                
                Row(
                    Column('phone', css_class='form-group col-md-3 mb-0'),
                    Column('fax', css_class='form-group col-md-3 mb-0'),
                    Column('mobile', css_class='form-group col-md-3 mb-0'),
                    css_class='form-row'
                ),
                Row(
                    Column('image', css_class='form-group col-md-12 mb-0'),
                    css_class='form-row'
                ),
                HTML('<br>'),
                Submit('save_user', _('Save & Close'), css_class='btn btn-primary fas fa-save'),
                Submit('save_user_new', _('Save & Edit'), css_class='btn btn-primary fas fa-save'),
                Reset('reset', 'Clear', css_class='btn btn-danger'),
                flush=True,
                always_open=True),
        ))

    class Meta:
        model = User
        exclude = ('date_created', 'date_modified', 'slug')

    def clean(self):
        cleaned_data = super(UserForm, self).clean()
        password = cleaned_data.get("password")
        username = cleaned_data.get("username")
        confirm_password = cleaned_data.get("confirm_password")
        
        first_active_date = cleaned_data.get("first_active_date")
        last_active_date = cleaned_data.get("last_active_date")

        if first_active_date >= last_active_date:
            raise forms.ValidationError(
                _("Last active date must be greater than First active date")
            )

        if username == "":
            raise forms.ValidationError(
                _("User Name must not be empty")
            )

        if password != confirm_password:
            raise forms.ValidationError(
                _("password and confirm password does not match")
            )


class RegisterForm(forms.ModelForm):
    email = forms.CharField(label='', max_length=100, widget=forms.EmailInput(attrs={'placeholder': _('Enter Email')}))
    password = forms.CharField(label='', widget=forms.PasswordInput(attrs={'placeholder': _('Enter Password')}))
    confirm_password = forms.CharField(label='', widget=forms.PasswordInput(attrs={'placeholder': _('Confirm Password')}))
    username = forms.CharField(label=_('Username'), widget=forms.TextInput(attrs={'placeholder': _('Enter Username')}))   
    date_joined = forms.DateTimeField(required=False)

    def __init__(self, *args, **kwargs):
        super(RegisterForm, self).__init__(*args, **kwargs)
        
        self.helper = FormHelper()
        self.helper.form_id = "user-form-id"
        self.helper.form_class = "user-form-class"
        self.helper.layout = Layout(
            'username', 
            'email',
            'password',
            'confirm_password',
                HTML('<hr>'),
                Submit('save_user', _('Sign Up'), css_class='btn btn-primary fas fa-save'),
                Reset('reset', 'Clear', css_class='btn btn-danger'),
        )

    class Meta:
        model = User
        exclude = ('date_created', 'date_modified', 'slug')

    def clean(self):
        cleaned_data = super(RegisterForm, self).clean()
        password = cleaned_data.get("password")
        username = cleaned_data.get("username")
        confirm_password = cleaned_data.get("confirm_password")

        if username == "":
            raise forms.ValidationError(
                _("User Name must not be empty")
            )

        if password != confirm_password:
            raise forms.ValidationError(
                _("password and confirm password does not match")
            )

# -*- coding: utf-8 -*-
from django import forms
from .models import (Bank, BankAccount)

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Submit, Row, Column, Reset, HTML, Field
from crispy_forms.bootstrap import FieldWithButtons, StrictButton, AccordionGroup, TabHolder, Tab
from django.utils.translation import ugettext_lazy as _
from crispy_bootstrap5.bootstrap5 import BS5Accordion


class BankForm(forms.ModelForm):

    parent = forms.ModelChoiceField(queryset=Bank.objects.all(), required=False)

    def __init__(self, *args, **kwargs):
        super(BankForm, self).__init__(*args, **kwargs)

        self.helper = FormHelper()
        self.helper.form_id = "bank-form-id"
        self.helper.form_class = "bank-form-class"
        self.helper.layout = Layout(
        HTML("""
            <p><strong style="font-size: 18px;">{}</strong></p>
            <hr>
        """.format(_('Add/Update Bank'),)),
        BS5Accordion(
            AccordionGroup(_('BANK MAIN DATA'),
                Row(
                    Column('name', css_class='form-group col-md-12 mb-0'),
                    css_class='form-row'
                    ),
                Row(
                    Column('address', css_class='form-group col-md-12 mb-0'),
                    css_class='form-row'
                ),
                Row(
                    Column('telephone', css_class='form-group col-md-4 mb-0'),
                    Column('fax', css_class='form-group col-md-4 mb-0'),
                    Column('cell', css_class='form-group col-md-4 mb-0'),
                css_class='form-row'
                ),
                Row(
                    Column('email', css_class='form-group col-md-4 mb-0'),
                    Column('website', css_class='form-group col-md-6 mb-0'),
                    Column('active_status', css_class='form-group col-md-2 mb-0'),
                css_class='form-row'),
                Row(
                    Column(Field('notes', rows='2'), css_class='form-group col-md-12 mb-0'),
                    css_class='form-row'),
            ),
                HTML('<br>'),
                Submit('save_bank', _('Save & Close'), css_class='btn btn-primary fas fa-save'),
                Submit('save_bank_new', _('Save & Edit'), css_class='btn btn-primary fas fa-save'),
                Reset('reset', 'Clear', css_class='btn btn-danger'),
                flush=True,
                always_open=True),
        )
    
    class Meta:
        model = Bank
        exclude = ('date_created', 'date_modified', 'slug', 'created_by', 'modified_by')


class BankAccountForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        super(BankAccountForm, self).__init__(*args, **kwargs)

        self.helper = FormHelper()
        self.helper.form_id = "bank_account-form-id"
        self.helper.form_class = "bank_account-form-class"
        self.helper.layout = Layout(
        HTML("""
            <p><strong style="font-size: 18px;">{}</strong></p>
            <hr>
        """.format(_('Add/Update Bank Account'),)),
        BS5Accordion(
            AccordionGroup(_('BANK ACCOUNT MAIN DATA'),
                Row(
                    Column('acc_no', css_class='form-group col-md-6 mb-0'),
                    FieldWithButtons('bank', StrictButton('',  css_class="btn fa fa-plus",
                    data_bs_toggle="modal", data_bs_target="#bank"), css_class='form-group col-md-4 mb-0'),
                    Column('acc_status', css_class='form-group col-md-2 mb-0'),
                    css_class='form-row'),
                Row(
                    Column('acc_nib', css_class='form-group col-md-3 mb-0'),
                    Column('acc_swift', css_class='form-group col-md-3 mb-0'),
                    Column('acc_iban', css_class='form-group col-md-3 mb-0'),
                    Column('acc_type', css_class='form-group col-md-3 mb-0'),
                css_class='form-row'
                ),
                Row(
                    Column(Field('notes', rows='2'), css_class='form-group col-md-12 mb-0'),
                    css_class='form-row'),
            ),
                HTML('<br>'),
                Submit('save_bank_account', _('Save & Close'), css_class='btn btn-primary fas fa-save'),
                Submit('save_bank_account_new', _('Save & Edit'), css_class='btn btn-primary fas fa-save'),
                Reset('reset', 'Clear', css_class='btn btn-danger'),
                flush=True,
                always_open=True),
        )

    class Meta:
        model = BankAccount
        exclude = ('date_created', 'date_modified', 'slug', 'created_by', 'modified_by')

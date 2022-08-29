# This file contains common functions for apps 
import datetime
from time import ctime
from decimal import Decimal

from django.db.models.functions import Extract
from django.db.models import F
from django.shortcuts import render, redirect, HttpResponseRedirect, get_object_or_404, HttpResponse
from django.contrib import messages #import messages
from django.utils.translation import ugettext_lazy as _
from bank.models import BankTransaction

current_date = datetime.date.today()
current_year = current_date.year
current_day = current_date.day
current_month = current_date.month
current_hour = ctime()

def save_bank_account(request, acc_id, debit, credit, notes):
    user = request.user
    created = datetime.datetime.now()

    BankTransaction.objects.create(account=acc_id, debit=debit, credit=credit, 
    notes=notes, date_created=created, date_modified=created, created_by=user, modified_by=user)
    
def get_model_field(model, model_field, search_field, return_field):
    """
    Returns the a field given the a field
    """

    try:
        model = model.objects.get(model_field=search_field)
        return model.return_field
    except model.DoesNotExist:
        return None

def handle_uploaded_file(f, dest):

    with open(dest, 'wb+') as destination:
        for chunk in f.chunks():
            destination.write(chunk)
            
            
# increments numbering in docs ex: Invoice, Receipt, and so on
def increment_invoice_number(model):
    '''
    Returns the current Document (Invoice, receipt, and so on) Number
    Restarts every year 
    '''
    # Returns the first object matched by the queryset, or None if there is no matching object.
    i = model.objects.filter(date_created__year=str(current_year)).order_by('-id').first()
    if i is not None:
        document_number = i.number + 1
    else:
        document_number = 1

    return document_number


# increments numbering in docs ex: Invoice, Receipt, and so on
def increment_document_number(model, document):
    # Returns the first object matched by the queryset, or None if there is no matching object. 
    i = model.objects.filter(document=document, date_created__year=str(current_year)).order_by('-id').first()
    if i is not None:
        document_number = i.number + 1
    else:
        document_number = 1

    return document_number


def make_payment(receipt_invoice_model, invoice_model, receipt_object, invoice, payment):
    
    if payment == "":
        return False

    if Decimal(payment) <= 0 or payment == 0:
        return False

    if not invoice: 
        return False

    # Total payment is equal or superior to debt
    if Decimal(payment) + invoice.credit >= invoice.total:
        payment = invoice.total - invoice.credit
        inv = invoice_model.objects.filter(id=invoice.id).update(
            credit=invoice.total,
            debit=0,
            paid_status=1
            )
    else:
        inv = invoice_model.objects.filter(id=invoice.id).update(
            credit=F('credit') + Decimal(payment),
            debit=F('debit') - Decimal(payment)
        )

    # Records the lines of Invoice
    r = receipt_invoice_model(receipt=receipt_object, invoice=invoice, debit=Decimal(invoice.debit),
    paid=Decimal(payment), remaining=invoice.debit-Decimal(payment), description=_(f"Invoice #{invoice.number} payment."))
    r.save()

    return inv


def handle_uploaded_file(f, dest):

    with open(dest, 'wb+') as destination:
        for chunk in f.chunks():
            destination.write(chunk)
            
            
    

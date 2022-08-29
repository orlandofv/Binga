# -*- coding: utf-8 -*-
import datetime
import json

from django.shortcuts import render
from django.contrib import messages #import messages
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.template.defaultfilters import slugify # new

from .models import Bank, BankAccount
from .forms import BankForm, BankAccountForm

# Create your views here.
@login_required
def bank_create_view(request):
    if request.method == 'POST':
        form = BankForm(request.POST)
        
        if form.is_valid():
            instance = form.save(commit=False)
            instance.created_by = instance.modified_by = request.user
            instance.date_created = instance.date_modified = datetime.datetime.now()
            instance = instance.save()

            messages.success(request, _("Bank added successfully!"))

            if request.POST.get('save_bank'):
                return redirect('bank:bank_list')
            else:
                return redirect('bank:bank_create')
        else:
            for error in form.errors.values():
                messages.error(request, error)
            return redirect('bank:bank_create')
    else:
        form = BankForm()
        context = {'form': form}
        return render(request, 'bank/createviews/bank_create.html', context)


@login_required
def bank_list_view(request):
    bank = Bank.objects.all()
    context = {}
    context['object_list'] = bank

    return render(request, 'bank/listviews/bank_list.html', context) 


@login_required
def bank_update_view(request, slug):
    bank = get_object_or_404(Bank, slug=slug)
    form = BankForm(request.POST or None, instance=bank)
	
    if request.method == 'POST':
        
        if form.is_valid():
            instance = form.save(commit=False)
            instance.modified_by = request.user
            instance.date_modified = datetime.datetime.now()
            instance = instance.save()

            messages.success(request, _("Bank updated successfully!"))

            if request.POST.get('save_bank'):
                return redirect('bank:bank_list')
            else:
                return redirect('bank:bank_create')

        else:
            for error in form.errors.values():
                messages.error(request, error)
            return redirect('bank:bank_update', slug=slug)
       
    context = {'form': form}
    return render(request, 'bank/updateviews/bank_update.html', context)


@login_required
def bank_delete_view(request):
    if request.is_ajax():
        selected_ids = request.POST['ckeck_box_item_ids']
        selected_ids = json.loads(selected_ids)
        for i, id in enumerate(selected_ids):
            if id != '':
                try:
                    Bank.objects.filter(id__in=selected_ids).delete()
                except Exception as e:
                    messages.warning(request, _("Not Deleted! {}".format(e)))
                    return redirect('bank:bank_list')
        
        messages.warning(request, _("Bank delete successfully!"))
        return redirect('bank:bank_list')


@login_required
def bank_detail_view(request, slug):
    # dictionary for initial data with
    # field names as keys
    bank = get_object_or_404(Bank, slug=slug)

    context ={}
    # add the dictionary during initialization
    context["bank"] = bank    
    return render(request, "bank/detailviews/bank_detail_view.html", context)


# Create your views here.
@login_required
def bank_account_create_view(request):
    if request.method == 'POST':
        form = BankAccountForm(request.POST)
        bank_form = BankForm(request.POST)
        
        if form.is_valid() or bank_form.is_valid():
            
            if request.POST.get('save_bank_new') or request.POST.get('save_bank'):
                instance = bank_form.save(commit=False)
                instance.created_by = instance.modified_by = request.user
                instance.date_created = instance.date_modified = datetime.datetime.now()
                instance = instance.save()
                return redirect('bank:bank_account_create')

            instance = form.save(commit=False)
            instance.created_by = instance.modified_by = request.user
            instance.date_created = instance.date_modified = datetime.datetime.now()
            instance = instance.save()

            messages.success(request, _("Bank Account added successfully!"))

            if request.POST.get('save_bank_account'):
                return redirect('bank:bank_account_list')
            else:
                return redirect('bank:bank_account_create')
        else:
            for error in bank_form.errors.values():
                messages.error(request, error)
            
            for error in form.errors.values():
                messages.error(request, error)
            return redirect('bank:bank_account_create')
    else:
        form = BankAccountForm()
        bank_form = BankForm()
        context = {'form': form, 'bank_form': bank_form}
        return render(request, 'bank/createviews/bank_account_create.html', context)


@login_required
def bank_account_list_view(request):
    bank_account = BankAccount.objects.all()
    context = {}
    context['object_list'] = bank_account

    return render(request, 'bank/listviews/bank_account_list.html', context) 


@login_required
def bank_account_update_view(request, slug):
    bank_account = get_object_or_404(BankAccount, slug=slug)
    form = BankAccountForm(request.POST or None, instance=bank_account)
    bank_form = BankForm(request.POST or None)
        
    if request.method == 'POST':
        if bank_form.is_valid():
            instance = bank_form.save(commit=False)
            instance.created_by = instance.modified_by = request.user
            instance.date_created = instance.date_modified = datetime.datetime.now()
            instance = instance.save()
            return redirect('bank:bank_account_create')
        else:
            for error in bank_form.errors.values():
                messages.error(request, error)
    
        if form.is_valid():
            instance = form.save(commit=False)
            instance.modified_by = request.user
            instance.date_modified = datetime.datetime.now()
            
            bank_id = request.POST.get('bank')
            bank_object = Bank.objects.get(id=int(bank_id))

            acc_no = request.POST.get('acc_no')  
            slug = slugify('{}, {}'.format(bank_object.name, acc_no))
            
            instance.slug = slug
            instance = instance.save()

            messages.success(request, _("Bank Account updated successfully!"))

            if request.POST.get('save_bank_account'):
                return redirect('bank:bank_account_list')
            else:
                return redirect('bank:bank_account_create')

        else:
            for error in form.errors.values():
                messages.error(request, error)
            return redirect('bank:bank_account_update', slug=slug)
       
    context = {'form': form}
    return render(request, 'bank/updateviews/bank_account_update.html', context)


@login_required
def bank_account_delete_view(request):
    if request.is_ajax():
        selected_ids = request.POST['ckeck_box_item_ids']
        selected_ids = json.loads(selected_ids)
        for i, id in enumerate(selected_ids):
            if id != '':
                try:
                    BankAccount.objects.filter(id__in=selected_ids).delete()
                except Exception as e:
                    messages.warning(request, _("Not Deleted! {}".format(e)))
                    return redirect('bank:bank_account_list')
        
        messages.warning(request, _("Bank Account delete successfully!"))
        return redirect('bank:bank_account_list')


@login_required
def bank_account_detail_view(request, slug):
    # dictionary for initial data with
    # field names as keys
    bank_account = get_object_or_404(BankAccount, slug=slug)

    context ={}
    # add the dictionary during initialization
    context["bank_account"] = bank_account    
    return render(request, "bank/detailviews/bank_account_detail_view.html", context)

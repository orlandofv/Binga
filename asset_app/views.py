# -*- coding: utf-8 -*-
import json
from multiprocessing import context
import pstats
import datetime
from decimal import Decimal
import os

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
from .models import (Component, Allocation, Maintenance, Item, 
MaintenanceItem, Costumer, Group, System, Type, 
SubType, Vendor, Settings, WorkOrder, Action)
from .filters import ComponentFilter
from users.models import User
from .forms import (ComponentForm, MaintenanceForm, CostumerForm, GroupForm, SystemForm, TypeForm, SubTypeForm, AllocationForm, 
VendorForm, ItemForm, SettingsForm, WorkOrderForm)
from django.contrib import messages #import messages
from django.utils.translation import ugettext_lazy as _
from config.settings import MEDIA_URL
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.http import JsonResponse
from django.core import serializers
from django.conf import settings


import qrcode

from utilities.utilities import handle_uploaded_file


########################## Settings ##########################
@login_required
def settings_create_view(request):
    obj = Settings.objects.first()
    form = SettingsForm(request.POST or None, request.FILES or None, instance=obj)

    if request.method == 'POST':
    
        if form.is_valid():
            instance = form.save(commit=False)
            instance.created_by = instance.modified_by = request.user
            instance.date_created = instance.date_modified = datetime.datetime.now()
            instance = instance.save()
            messages.success(request, _("Settings added successfully!"))

            if request.POST.get('save_settings'):
                return redirect('asset_app:home')
            else:
                return redirect('asset_app:settings_create')
        else:
            for error in form.errors.values():
                messages.error(request, error)
            return redirect('asset_app:settings_create')
    
    context = {'form': form}
    return render(request, 'asset_app/createviews/settings_create.html', context)


@login_required
def home_view(request):
    context = {
        'component': Component.objects.all(), 
        'maitntenance': Maintenance.objects.all(), 
        'costumer': Costumer.objects.all(),  
        'allocation': Allocation.objects.all(), 
        'group': Group.objects.all(), 
        'system': System.objects.all(), 
        'type': Type.objects.all(), 
        'subtype': SubType.objects.all(), 
        'vendor': Vendor.objects.all(), 
        'item': Item.objects.all(), 
        'settings': Settings.objects.all(),
    }
    return render(request, 'index.html', context)


########################## Maintenance ##########################
class MaintenanceListView(LoginRequiredMixin, ListView):
    template_name = 'asset_app/listviews/maintenance_list_view.html'
    queryset = Maintenance.objects.order_by('-date_modified') 


@login_required
def maintenance_create_view(request):
    if request.method == 'POST':
        form = MaintenanceForm(request.POST)
        if form.is_valid():
            instance = form.save(commit=False)
            instance.created_by = instance.modified_by = request.user
            instance.date_created = instance.date_modified = datetime.datetime.now()
            maintenance = instance
            instance = instance.save()
            
            slug = slugify('{}-{}'.format(maintenance.name, maintenance.type))
            
            # Saves actions
            save_action(request, maintenance)
            save_item(request, maintenance)

            messages.success(request, _("Maintenance added successfully!"))

            if request.POST.get('save_maintenance'):
                return redirect('asset_app:maintenance_details', slug=slug)
            else:
                return redirect('asset_app:maintenance_create')
        else:
            for error in form.errors.values():
                messages.error(request, error)
            return redirect('asset_app:maintenance_create')
    else:
        form = MaintenanceForm()
        context = {'form': form}
        return render(request, 'asset_app/createviews/maintenance_create.html', context)


def save_action(request, instance):

    post = dict(request.POST)
    actions = post['action']

    i = 0
    for c in actions:
        try:
            if c != "":
                action_object = Action(name=c, maintenance=instance, slug=slugify(c), 
                date_created=datetime.datetime.now(), date_modified=datetime.datetime.now(), 
                created_by=request.user, modified_by=request.user)

                action_object.save()
        except IntegrityError:
            if c != "":
                action_object = Action.objects.filter(name=c, maintenance=instance).update(slug=slugify(c), 
                date_modified=datetime.datetime.now(), modified_by=request.user)
                
        i += 1

    return request


def save_item(request, instance):

    post = dict(request.POST)
    items = post['item']
    costs = post['cost']
    qt = post['quantity']
    unit = post['unit']

    i = 0
    for c in items:
        print(c)

        if c != "":
            try:
                item_object = Item(name=c, slug=slugify(c), cost=costs[i], quantity=qt[i], unit=unit[i],
                date_created=datetime.datetime.now(), date_modified=datetime.datetime.now(), 
                created_by=request.user, modified_by=request.user)
                _item = item_object.save()
            except IntegrityError as e:
                item_object = Item.objects.filter(name=c).update(slug=slugify(c), cost=costs[i], 
                quantity=qt[i], unit=unit[i], date_modified=datetime.datetime.now(), 
                modified_by=request.user)
                _item = Item.objects.get(name=c)

            try:
                maintenance_item_object = MaintenanceItem(maintenance=instance, item=_item, 
                quantity=qt[i], cost=costs[i])
                maintenance_item_object.save()

            except IntegrityError:
                maintenance_item_object = MaintenanceItem.objects.filter(item=_item, 
                maintenance=instance).update(quantity=qt[i], cost=costs[i])

        i += 1

    return request


@login_required
def maintenance_update_view(request, slug):
    maintenance = get_object_or_404(Maintenance, slug=slug)
    form = MaintenanceForm(request.POST or None, instance=maintenance)

    if request.method == 'POST':

        if form.is_valid():
            instance = form.save(commit=False)
            instance.modified_by = request.user
            slug = slugify('{}-{}'.format(instance.name, instance.type))
            print(slug)
            instance.slug = slug
            instance.date_modified = datetime.datetime.now()
            try:
                instance = instance.save()
            except IntegrityError as e:
                messages.error(request, e)
                return redirect('asset_app:maintenance_update', slug=slug)

             # Saves actions
            save_action(request, maintenance)
            save_item(request, maintenance)

            messages.success(request, _("Maintenance updated successfully!"))

            if request.POST.get('save_maintenance'):
                return redirect('asset_app:maintenance_details', slug=slug)
            else:
                return redirect('asset_app:maintenance_create')

        else:
            for error in form.errors.values():
                messages.error(request, error)
            return redirect('asset_app:maintenance_update', slug=slug)

    actions = Action.objects.filter(maintenance=maintenance)
    items = MaintenanceItem.objects.filter(maintenance=maintenance).select_related('item')

    context = {'form': form, 'items': items, 'actions': actions, 'maintenance': maintenance}
    return render(request, 'asset_app/updateviews/maintenance_update.html', context)


@login_required
def maintenance_delete_view(request):
    if request.is_ajax():
        selected_ids = request.POST['check_box_item_ids']
        selected_ids = json.loads(selected_ids)
        for i, id in enumerate(selected_ids):
            if id != '':
                try:
                    Maintenance.objects.filter(id__in=selected_ids).delete()
                except Exception as e:
                    messages.warning(request, _("Not Deleted! {}".format(e)))
                    return redirect('asset_app:maintenance_list')

        messages.warning(request, _("Maintenance delete successfully!"))
        return redirect('asset_app:maintenance_list')


def maintenance_dashboard_view(request):
    ROUTINE = 'Routine'
    PREVENTIVE = 'Preventive'
    CORRECTIVE = 'Corrective'
    PREDECTIVE = 'Predective'

    last_maintenances =  Maintenance.objects.all().order_by('-date_created')[:15]
    total_maintenances =  Maintenance.objects.all().count()
    all_maintenances = Maintenance.objects.all().order_by('name')
    preventive_maintenances = Allocation.component.maintenance.objects.filter(type=PREVENTIVE).count()
    routine_maintenances = Maintenance.objects.filter(type=ROUTINE).count()
    corrective_maintenances = Maintenance.objects.filter(type=CORRECTIVE).count()
    predective_maintenances = Maintenance.objects.filter(type=PREDECTIVE).count()
    
    context = {}
    context['total'] = total_maintenances
    context['last'] = last_maintenances
    context['all'] = all_maintenances
    context['preventive'] = preventive_maintenances
    context['routine'] = routine_maintenances
    context['corrective'] = corrective_maintenances
    context['predective'] = predective_maintenances

    return render(request, 'asset_app/dashboardviews/maintenance_dashboard.html', context=context)


@login_required
def maintenance_detail_view(request, slug):
    # dictionary for initial data with
    # field names as keys
    maintenance = get_object_or_404(Maintenance, slug=slug)
    
    actions = Action.objects.filter(maintenance=maintenance)
    items = MaintenanceItem.objects.filter(maintenance=maintenance).select_related('item')
    
    # Related Maintenances
    related = Maintenance.objects.filter(name=maintenance.name).exclude(type=maintenance.type)

    context ={}
    # add the dictionary during initialization
    context["maintenance"] = maintenance    
    context["items"] = items    
    context["actions"] = actions    
    context["related"] = related    
    return render(request, "asset_app/detailviews/maintenance_detail_view.html", context)


@login_required
def maintenance_item_create_view(request, slug):

    maintenance = get_object_or_404(Maintenance, slug=slug)
    items = MaintenanceItem.objects.filter(maintenance=maintenance)

    if request.method == 'POST':
        form = ItemForm(request.POST)

        # Get the object from the form
        obj = request.POST.get('name')
        
        try:
            item_object = Item.objects.get(name=obj)
        except Exception as e:
            print(e)
            item_object = None

        quantity = Decimal(request.POST.get('quantity'))

        # save the data and after fetch the object in instance
        if item_object:
            item = Item.objects.get(name=obj)
            try:
                instance = MaintenanceItem(maintenance=maintenance, item=item, quantity=quantity) 
                instance.save()

            except Exception as e:
                print(e)
                messages.error(request, _('Item with this name already exists'))
                return render(request, 'asset_app/createviews/item_create.html', 
                {'maintenance': maintenance, 'form': form, 'items': items})
        else:
            item = Item()
            item.name = obj
            item.quantity = Decimal(request.POST.get('quantity'))
            item.created_by =  item.modified_by = request.user
            item.date_created = item.date_modified = datetime.datetime.now()

            try:
                item.save()
                m =  MaintenanceItem(maintenance=maintenance, item=item, quantity=quantity)
                m.save()
            except Exception as e:
                print(e)
                messages.error(request, _('Item with this name already exists'))
                return render(request, 'asset_app/createviews/item_create.html', 
                {'maintenance': maintenance, 'form': form, 'items': items})

        messages.success(request, _("'{}' added successfully!".format(item.name)))
        return redirect('asset_app:item_create', slug=slug)
    else:
        form = ItemForm(None)
        return render(request, 'asset_app/createviews/item_create.html', 
        {'maintenance': maintenance, 'form': form, 'items': items})

@login_required
def maintenance_item_delete_view(request):
    if request.is_ajax():
        selected_ids = request.POST['check_box_item_ids']
        selected_ids = json.loads(selected_ids)
        print(selected_ids)

        for i, id in enumerate(selected_ids):
            if id != '':
                try:
                    MaintenanceItem.objects.filter(id__in=selected_ids).delete()
                except Exception as e:
                    messages.warning(request, _("Not Deleted! {}.".format(e)))
                    return redirect('asset_app:home')

        return redirect('asset_app:home')


@login_required
def maintenance_action_delete_view(request):
    if request.is_ajax():
        selected_ids = request.POST['check_box_item_ids']
        selected_ids = json.loads(selected_ids)
        for i, id in enumerate(selected_ids):
            if id != '':
                try:
                    Action.objects.filter(id__in=selected_ids).delete()
                except Exception as e:
                    messages.warning(request, _("Not Deleted! {}".format(e)))
                    return redirect('asset_app:home')

        return redirect('asset_app:home')

########################## Component ##########################
class ComponentListView(LoginRequiredMixin, ListView):
    model = Component
    template_name = 'asset_app/listviews/component_list_view.html'

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super().get_context_data(**kwargs)
        # Add in a QuerySet of all the books
        components = Component.objects.all()

        c = {}
        for x in components:
            c['component_no'] = x.component_no 
            c['name'] = x.name 
            c['slug'] = x.slug 
            c['manufacturer'] = x.manufacturer 
            c['stock_code'] = x.stock_code 
            c['maintenance'] = x.maintenance 
            c['image'] = x.image  
            c['notes'] = x.notes  
            c['date_created'] = x.date_created  
            c['date_modified'] = x.date_modified  
            c['created_by'] = x.created_by 
            c['modified_by'] = x.modified_by  

        context['allocation'] = Allocation.objects.all()
        context['data'] = c
        return context


@login_required
def component_create_view(request):
    if request.method == 'POST':
        form = ComponentForm(request.POST)
        maintenance_form = MaintenanceForm(request.POST)

        if form.is_valid() or maintenance_form.is_valid():
            if request.POST.get('save_maintenance') or request.POST.get('save_maintenance_new'):
                instance = maintenance_form.save(commit=False)
                instance.created_by = instance.modified_by = request.user
                instance.date_created = instance.date_modified = datetime.datetime.now()
                instance = instance.save()
                return redirect('asset_app:component_create')
            else:
                instance = form.save(commit=False)
                instance.created_by = instance.modified_by = request.user
                instance.date_created = instance.date_modified = datetime.datetime.now()
                instance = instance.save()
                messages.success(request, _("Component added successfully!"))

                if request.POST.get('save_component'):
                    return redirect('asset_app:component_list')
                else:
                    return redirect('asset_app:component_create')
        else:
            for error in form.errors.values():
                messages.error(request, error)
            return redirect('asset_app:component_create')
    else:
        form = ComponentForm()
        maintenance_form = MaintenanceForm()
        context = {'form': form, 'maintenance_form': maintenance_form}
        return render(request, 'asset_app/createviews/component_create.html', context)


@login_required
def component_dashboard_view(request):
    
    GOOD = 'Good'
    BROKEN = 'Broken'
    
    last_components =  Component.objects.all().order_by('-date_created')[:15]
    total_components =  Component.objects.all().count()
    all_components = Component.objects.all().order_by('name')
    broken_components = Allocation.objects.filter(status=BROKEN).count()
    good_components = Allocation.objects.filter(status=GOOD).count()

    cursor = connection.cursor()
    print(cursor)
    cursor.execute("""SELECT DISTINCT component_id FROM asset_app_allocation
    GROUP BY component_id""")
    data = cursor.fetchall()
    allocated_components = len(data)
    
    context = {}
    context['total'] = total_components
    context['last'] = last_components
    context['all'] = all_components
    context['broken'] = broken_components
    context['good'] = good_components
    context['allocated'] = allocated_components
    context['not_allocated'] = total_components - allocated_components
   
    return render(request, 'asset_app/dashboardviews/component_dashboard.html', context=context)


@login_required
def component_update_view(request, slug):
    component = get_object_or_404(Component, slug=slug)
    form = ComponentForm(request.POST or None, instance=component)
    maintenance_form = MaintenanceForm(request.POST or None)

    if request.method == 'POST':

        if form.is_valid():
            instance = form.save(commit=False)
            instance.modified_by = request.user
            instance.slug = slugify(instance.name)
            instance.date_modified = datetime.datetime.now()
            instance = instance.save()
            messages.success(request, _("Component updated successfully!"))

            if request.POST.get('save_component'):
                return redirect('asset_app:component_list')
            else:
                return redirect('asset_app:component_create')

        else:
            for error in form.errors.values():
                messages.error(request, error)
            return redirect('asset_app:component_update', slug=slug)
       
    context = {'form': form, 'maintenance_form': maintenance_form}
    return render(request, 'asset_app/updateviews/component_update.html', context)


@login_required
def component_delete_view(request):
    if request.is_ajax():
        selected_ids = request.POST['check_box_item_ids']
        selected_ids = json.loads(selected_ids)
        for i, id in enumerate(selected_ids):
            if id != '':
                try:
                    Component.objects.filter(id__in=selected_ids).delete()
                except Exception as e:
                    messages.warning(request, _("Not Deleted! {}".format(e)))
                    return redirect('asset_app:component_list')
        
        messages.warning(request, _("Component delete successfully!"))
        return redirect('asset_app:component_list')


@login_required
def component_detail_view(request, slug):
    # dictionary for initial data with
    # field names as keys
    component = get_object_or_404(Component, slug=slug)
   
    context ={}
    # add the dictionary during initialization
    context["data"] = component    
    return render(request, "asset_app/detailviews/component_detail_view.html", context)


########################## Costumer ##########################
class CostumerListView(LoginRequiredMixin, ListView):
    queryset = Costumer.objects.filter(is_costumer=1)
    template_name = 'asset_app/listviews/costumer_list_view.html'


@login_required
def costumer_create_view(request):
    if request.method == 'POST':

        form = CostumerForm(request.POST)
        if form.is_valid():
            instance = form.save(commit=False)
            
            parent = request.POST.get('parent')
            
            if parent == "":
                instance.parent = 0
            else:
                instance.parent = parent

            instance.created_by = instance.modified_by = request.user
            instance.date_created = instance.date_modified = datetime.datetime.now()
            instance.is_costumer = 1
            instance = instance.save()
            
            messages.success(request, _("Costumer added successfully!"))

            if request.POST.get('save_costumer'):
                return redirect('asset_app:costumer_list')
            else:
                return redirect('asset_app:costumer_create')
        else:
            print(form.errors)
            for error in form.errors.values():
                messages.error(request, error)
            return redirect('asset_app:costumer_create')
    else:
        form = CostumerForm()
        context = {'form': form}
        return render(request, 'asset_app/createviews/costumer_create.html', context)


@login_required
def costumer_update_view(request, slug):
    costumer = get_object_or_404(Costumer, slug=slug)
    form = CostumerForm(request.POST or None, instance=costumer)

    if request.method == 'POST':
        
        if form.is_valid():
            print(request.POST)
            
            instance = form.save(commit=False)
            instance.modified_by = request.user
            instance.slug = slugify(instance.name)
            instance.date_modified = datetime.datetime.now()
            instance.is_costumer = 1
            parent = request.POST.get('parent')
            if parent == "":
                instance.parent = 0
            else:
                instance.parent = parent

            instance = instance.save()
            messages.success(request, _("Costumer updated successfully!"))

            if request.POST.get('save_costumer'):
                return redirect('asset_app:costumer_list')
            else:
                return redirect('asset_app:costumer_create')

        else:
            print(form.errors)
            for error in form.errors.values():
                messages.error(request, error)
            return redirect('asset_app:costumer_update', slug=slug)
       
    context = {'form': form}
    return render(request, 'asset_app/updateviews/costumer_update.html', context)


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
                    return redirect('asset_app:costumer_list')
        
        messages.warning(request, _("Costumer delete successfully!"))
        return redirect('asset_app:costumer_list')


@login_required
def costumer_detail_view(request, slug):
    # dictionary for initial data with
    # field names as keys
    costumer = get_object_or_404(Costumer, slug=slug)
   
    context ={}
    # add the dictionary during initialization
    context["data"] = costumer    
    return render(request, "asset_app/detailviews/costumer_detail_view.html", context)


########################## Group ##########################
class GroupListView(LoginRequiredMixin, ListView):
    model = Group
    template_name = 'asset_app/listviews/group_list_view.html'


@login_required
def group_create_view(request):
    if request.method == 'POST':
        form = GroupForm(request.POST)
        if form.is_valid():
            instance = form.save(commit=False)
            instance.created_by = instance.modified_by = request.user
            instance.date_created = instance.date_modified = datetime.datetime.now()
            instance = instance.save()
            messages.success(request, _("Group added successfully!"))

            if request.POST.get('save_group'):
                return redirect('asset_app:group_list')
            else:
                return redirect('asset_app:group_create')
        else:
            for error in form.errors.values():
                messages.error(request, error)
            return redirect('asset_app:group_create')
    else:
        form = GroupForm()
        context = {'form': form}
        return render(request, 'asset_app/createviews/group_create.html', context)


@login_required
def group_update_view(request, slug):
    group = get_object_or_404(Group, slug=slug)
    form = GroupForm(request.POST or None, instance=group)

    if request.method == 'POST':
        

        if form.is_valid():
            instance = form.save(commit=False)
            instance.modified_by = request.user
            instance.slug = slugify(instance.name)
            instance.date_modified = datetime.datetime.now()
            instance = instance.save()
            messages.success(request, _("Group updated successfully!"))

            if request.POST.get('save_group'):
                return redirect('asset_app:group_list')
            else:
                return redirect('asset_app:group_create')

        else:
            for error in form.errors.values():
                messages.error(request, error)
            return redirect('asset_app:group_update', slug=slug)
       
    context = {'form': form}
    return render(request, 'asset_app/updateviews/group_update.html', context)


@login_required
def group_delete_view(request):
    if request.is_ajax():
        selected_ids = request.POST['check_box_item_ids']
        selected_ids = json.loads(selected_ids)
        for i, id in enumerate(selected_ids):
            if id != '':
                try:
                    Group.objects.filter(id__in=selected_ids).delete()
                except Exception as e:
                    messages.warning(request, _("Not Deleted! {}".format(e)))
                    return redirect('asset_app:group_list')
        
        messages.warning(request, _("Group delete successfully!"))
        return redirect('asset_app:group_list')


@login_required
def group_detail_view(request, slug):
    # dictionary for initial data with
    # field names as keys
    group = get_object_or_404(Group, slug=slug)
   
    context ={}
    # add the dictionary during initialization
    context["data"] = group    
    return render(request, "asset_app/detailviews/group_detail_view.html", context)


########################## System ##########################
class SystemListView(LoginRequiredMixin, ListView):
    model = System
    template_name = 'asset_app/listviews/system_list_view.html'


@login_required
def system_create_view(request):
    if request.method == 'POST':
        form = SystemForm(request.POST)
        group_form = GroupForm(request.POST)

        if form.is_valid() or group_form.is_valid():
            if request.POST.get('save_group') or request.POST.get('save_group_new'):
                instance = group_form.save(commit=False)
                instance.created_by = instance.modified_by = request.user
                instance.date_created = instance.date_modified = datetime.datetime.now()
                instance = instance.save()
                return redirect('asset_app:system_create')
            else:
                instance = form.save(commit=False)
                instance.created_by = instance.modified_by = request.user
                instance.date_created = instance.date_modified = datetime.datetime.now()
                instance = instance.save()
                messages.success(request, _("System added successfully!"))

                if request.POST.get('save_system'):
                    return redirect('asset_app:system_list')
                else:
                    return redirect('asset_app:system_create')
        else:
            for error in form.errors.values():
                messages.error(request, error)
            return redirect('asset_app:system_create')
    else:
        form = SystemForm()
        group_form = GroupForm()
        context = {'form': form, 'group_form': group_form}
        return render(request, 'asset_app/createviews/system_create.html', context)


@login_required
def system_update_view(request, slug):
    system = get_object_or_404(System, slug=slug)
    form = SystemForm(request.POST or None, instance=system)
    group_form = GroupForm(request.POST or None)

    if request.method == 'POST':
        

        if form.is_valid():
            instance = form.save(commit=False)
            instance.modified_by = request.user
            instance.slug = slugify(instance.name)
            instance.date_modified = datetime.datetime.now()
            instance = instance.save()
            messages.success(request, _("System updated successfully!"))

            if request.POST.get('save_system'):
                return redirect('asset_app:system_list')
            else:
                return redirect('asset_app:system_create')

        else:
            for error in form.errors.values():
                messages.error(request, error)
            return redirect('asset_app:system_update', slug=slug)
       
    context = {'form': form, 'group_form': group_form}
    return render(request, 'asset_app/updateviews/system_update.html', context)


@login_required
def system_delete_view(request):
    if request.is_ajax():
        selected_ids = request.POST['check_box_item_ids']
        selected_ids = json.loads(selected_ids)
        for i, id in enumerate(selected_ids):
            if id != '':
                try:
                    System.objects.filter(id__in=selected_ids).delete()
                except Exception as e:
                    messages.warning(request, _("Not Deleted! {}".format(e)))
                    return redirect('asset_app:system_list')
        
        messages.warning(request, _("System delete successfully!"))
        return redirect('asset_app:system_list')


@login_required
def system_detail_view(request, slug):
    # dictionary for initial data with
    # field names as keys
    system = get_object_or_404(System, slug=slug)
   
    context ={}
    # add the dictionary during initialization
    context["data"] = system    
    return render(request, "asset_app/detailviews/system_detail_view.html", context)


########################## Type ##########################
class TypeListView(LoginRequiredMixin, ListView):
    model = Type
    template_name = 'asset_app/listviews/type_list_view.html'


def type_create_view(request):
    if request.method == 'POST':
        form = TypeForm(request.POST)
        system_form = SystemForm(request.POST)

        if form.is_valid() or system_form.is_valid():
            if request.POST.get('save_system') or request.POST.get('save_system_new'):
                instance = system_form.save(commit=False)
                instance.created_by = instance.modified_by = request.user
                instance.date_created = instance.date_modified = datetime.datetime.now()
                instance = instance.save()
                return redirect('asset_app:type_create')
            else:
                instance = form.save(commit=False)
                instance.created_by = instance.modified_by = request.user
                instance.date_created = instance.date_modified = datetime.datetime.now()
                instance = instance.save()
                messages.success(request, _("Type added successfully!"))

                if request.POST.get('save_type'):
                    return redirect('asset_app:type_list')
                else:
                    return redirect('asset_app:type_create')
        else:
            for error in form.errors.values():
                messages.error(request, error)
            return redirect('asset_app:type_create')
    else:
        form = TypeForm()
        system_form = SystemForm()
        context = {'form': form, 'system_form': system_form}
        return render(request, 'asset_app/createviews/type_create.html', context)


@login_required
def type_update_view(request, slug):
    type = get_object_or_404(Type, slug=slug)
    form = TypeForm(request.POST or None, instance=type)
    system_form = SystemForm(request.POST or None)

    if request.method == 'POST':
        

        if form.is_valid():
            instance = form.save(commit=False)
            instance.modified_by = request.user
            instance.slug = slugify(instance.name)
            instance.date_modified = datetime.datetime.now()
            instance = instance.save()
            messages.success(request, _("Type updated successfully!"))

            if request.POST.get('save_type'):
                return redirect('asset_app:type_list')
            else:
                return redirect('asset_app:type_create')

        else:
            for error in form.errors.values():
                messages.error(request, error)
            return redirect('asset_app:type_update', slug=slug)
       
    context = {'form': form, 'system_form': system_form}
    return render(request, 'asset_app/updateviews/type_update.html', context)


@login_required
def type_delete_view(request):
    if request.is_ajax():
        selected_ids = request.POST['check_box_item_ids']
        selected_ids = json.loads(selected_ids)
        for i, id in enumerate(selected_ids):
            if id != '':
                try:
                    Type.objects.filter(id__in=selected_ids).delete()
                except Exception as e:
                    messages.warning(request, _("Not Deleted! {}".format(e)))
                    return redirect('asset_app:type_list')
        
        messages.warning(request, _("Type delete successfully!"))
        return redirect('asset_app:type_list')


@login_required
def type_detail_view(request, slug):
    # dictionary for initial data with
    # field names as keys
    type = get_object_or_404(Type, slug=slug)
   
    context ={}
    # add the dictionary during initialization
    context["data"] = type    
    return render(request, "asset_app/detailviews/type_detail_view.html", context)


########################## SubType ##########################
class SubTypeListView(LoginRequiredMixin, ListView):
    model = SubType
    template_name = 'asset_app/listviews/subtype_list_view.html'


@login_required
def subtype_create_view(request):
    if request.method == 'POST':
        form = SubTypeForm(request.POST)
        type_form = TypeForm(request.POST)

        if form.is_valid() or type_form.is_valid():
            if request.POST.get('save_type') or request.POST.get('save_type_new'):
                instance = type_form.save(commit=False)
                instance.created_by = instance.modified_by = request.user
                instance.date_created = instance.date_modified = datetime.datetime.now()
                instance = instance.save()
                return redirect('asset_app:subtype_create')
            else:
                instance = form.save(commit=False)
                instance.created_by = instance.modified_by = request.user
                instance.date_created = instance.date_modified = datetime.datetime.now()
                instance = instance.save()
                messages.success(request, _("SubType added successfully!"))

                if request.POST.get('save_subtype'):
                    return redirect('asset_app:subtype_list')
                else:
                    return redirect('asset_app:subtype_create')
        else:
            for error in form.errors.values():
                messages.error(request, error)
            return redirect('asset_app:subtype_create')
    else:
        form = SubTypeForm()
        type_form = TypeForm()
        context = {'form': form, 'type_form': type_form}
        return render(request, 'asset_app/createviews/subtype_create.html', context)


@login_required
def subtype_update_view(request, slug):
    subtype = get_object_or_404(SubType, slug=slug)
    form = SubTypeForm(request.POST or None, instance=subtype)
    type_form = TypeForm(request.POST or None)

    if request.method == 'POST':
        

        if form.is_valid():
            instance = form.save(commit=False)
            instance.modified_by = request.user
            instance.slug = slugify(instance.name)
            instance.date_modified = datetime.datetime.now()
            instance = instance.save()
            messages.success(request, _("SubType updated successfully!"))

            if request.POST.get('save_subtype'):
                return redirect('asset_app:subtype_list')
            else:
                return redirect('asset_app:subtype_create')

        else:
            for error in form.errors.values():
                messages.error(request, error)
            return redirect('asset_app:subtype_update', slug=slug)
       
    context = {'form': form, 'type_form': type_form}
    return render(request, 'asset_app/updateviews/subtype_update.html', context)


@login_required
def subtype_delete_view(request):
    if request.is_ajax():
        selected_ids = request.POST['check_box_item_ids']
        selected_ids = json.loads(selected_ids)
        for i, id in enumerate(selected_ids):
            if id != '':
                try:
                    SubType.objects.filter(id__in=selected_ids).delete()
                except Exception as e:
                    messages.warning(request, _("Not Deleted! {}".format(e)))
                    return redirect('asset_app:subtype_list')
        
        messages.warning(request, _("SubType delete successfully!"))
        return redirect('asset_app:subtype_list')


@login_required
def subtype_detail_view(request, slug):
    # dictionary for initial data with
    # field names as keys
    subtype = get_object_or_404(SubType, slug=slug)
   
    context ={}
    # add the dictionary during initialization
    context["data"] = subtype    
    return render(request, "asset_app/detailviews/subtype_detail_view.html", context)


########################## Vendor ##########################
class VendorListView(LoginRequiredMixin, ListView):
    model = Vendor
    template_name = 'asset_app/listviews/vendor_list_view.html'


@login_required
def vendor_create_view(request):
    if request.method == 'POST':
        form = VendorForm(request.POST)
        if form.is_valid():
            instance = form.save(commit=False)
            instance.created_by = instance.modified_by = request.user
            instance.date_created = instance.date_modified = datetime.datetime.now()
            instance = instance.save()
            messages.success(request, _("Vendor added successfully!"))

            if request.POST.get('save_vendor'):
                return redirect('asset_app:vendor_list')
            else:
                return redirect('asset_app:vendor_create')
        else:
            for error in form.errors.values():
                messages.error(request, error)
            return redirect('asset_app:vendor_create')
    else:
        form = VendorForm()
        context = {'form': form}
        return render(request, 'asset_app/createviews/vendor_create.html', context)


@login_required
def vendor_update_view(request, slug):
    vendor = get_object_or_404(Vendor, slug=slug)
    form = VendorForm(request.POST or None, instance=vendor)

    if request.method == 'POST':
        

        if form.is_valid():
            instance = form.save(commit=False)
            instance.modified_by = request.user
            instance.slug = slugify(instance.name)
            instance.date_modified = datetime.datetime.now()
            instance = instance.save()
            messages.success(request, _("Vendor updated successfully!"))

            if request.POST.get('save_vendor'):
                return redirect('asset_app:vendor_list')
            else:
                return redirect('asset_app:vendor_create')

        else:
            for error in form.errors.values():
                messages.error(request, error)
            return redirect('asset_app:vendor_update', slug=slug)
       
    context = {'form': form}
    return render(request, 'asset_app/updateviews/vendor_update.html', context)


@login_required
def vendor_delete_view(request):
    if request.is_ajax():
        selected_ids = request.POST['check_box_item_ids']
        selected_ids = json.loads(selected_ids)
        for i, id in enumerate(selected_ids):
            if id != '':
                try:
                    Vendor.objects.filter(id__in=selected_ids).delete()
                except Exception as e:
                    messages.warning(request, _("Not Deleted! {}".format(e)))
                    return redirect('asset_app:vendor_list')
        
        messages.warning(request, _("Vendor delete successfully!"))
        return redirect('asset_app:vendor_list')


@login_required
def vendor_detail_view(request, slug):
    # dictionary for initial data with
    # field names as keys
    vendor = get_object_or_404(Vendor, slug=slug)
   
    context ={}
    # add the dictionary during initialization
    context["data"] = vendor    
    return render(request, "asset_app/detailviews/vendor_detail_view.html", context)


########################## Allocation ##########################
class AllocationListView(LoginRequiredMixin, ListView):
    model = Allocation
    template_name = 'asset_app/listviews/allocation_list_view.html'


@login_required
def allocation_create_view(request):

    if request.method == 'POST':
        form = AllocationForm(request.POST, request.FILES)
        component_form = ComponentForm(request.POST)
        costumer_form = CostumerForm(request.POST)
        group_form = GroupForm(request.POST)
        system_form = SystemForm(request.POST)
        type_form = TypeForm(request.POST)
        subtype_form = SubTypeForm(request.POST)
        vendor_form = VendorForm(request.POST)

        if form.is_valid() or costumer_form.is_valid() or component_form.is_valid() \
            or group_form.is_valid() or system_form.is_valid() or type_form.is_valid() \
                    or subtype_form.is_valid() or vendor_form.is_valid():

            if request.POST.get('save_component') or request.POST.get('save_component_new'):
                instance = component_form.save(commit=False)
            
            if request.POST.get('save_costumer') or request.POST.get('save_costumer_new'):
                instance = costumer_form.save(commit=False)
            
            if request.POST.get('save_group') or request.POST.get('save_group_new'):
                instance = group_form.save(commit=False)
            
            if request.POST.get('save_system') or request.POST.get('save_system_new'):
                instance = system_form.save(commit=False)
            
            if request.POST.get('save_type') or request.POST.get('save_type_new'):
                instance = type_form.save(commit=False)
            
            if request.POST.get('save_subtype') or request.POST.get('save_subtype_new'):
                instance = subtype_form.save(commit=False)
            
            if request.POST.get('save_vendor') or request.POST.get('save_vendor_new'):
                instance = vendor_form.save(commit=False)
            
            if request.POST.get('save_allocation') or request.POST.get('save_allocation_new'):
                instance = form.save(commit=False)

                try:
                    qrcode = create_qrcode(request, instance)
                    instance.qrcode = qrcode
                except Exception as e:
                    print(f'Error: {e}')

            
                messages.success(request, _("Allocation created successfully!"))

            instance.created_by = instance.modified_by = request.user
            instance.date_created = instance.date_modified = datetime.datetime.now()
            instance = instance.save()
    
            if request.POST.get('save_allocation'):
                return redirect('asset_app:allocation_list')
            else:
                return redirect('asset_app:allocation_create')

        else:
            for error in form.errors.values():
                messages.error(request, error)
            return redirect('asset_app:allocation_create')
    else:
        form = AllocationForm()
        component_form = ComponentForm()
        costumer_form = CostumerForm()
        group_form = GroupForm()
        system_form = SystemForm()
        type_form = TypeForm()
        subtype_form = SubTypeForm()
        vendor_form = VendorForm()

        context = {'form': form, 'component_form': component_form,'costumer_form': costumer_form, 
        'group_form': group_form, 'system_form': system_form, 'type_form': type_form, 
        'subtype_form': subtype_form, 'vendor_form': vendor_form}
        return render(request, 'asset_app/createviews/allocation_create.html', context)


@login_required
def allocation_update_view(request, slug):
    allocation = get_object_or_404(Allocation, slug=slug)
    form = AllocationForm(request.POST or None, request.FILES or None, instance=allocation)
    component_form = ComponentForm(request.POST or None)
    costumer_form = CostumerForm(request.POST or None)
    group_form = GroupForm(request.POST or None)
    system_form = SystemForm(request.POST or None)
    type_form = TypeForm(request.POST or None)
    subtype_form = SubTypeForm(request.POST or None)
    vendor_form = VendorForm(request.POST or None)

    if request.method == 'POST':
        try:
            if form.is_valid() or costumer_form.is_valid() or component_form.is_valid() \
                or group_form.is_valid() or system_form.is_valid() or type_form.is_valid() \
                        or subtype_form.is_valid() or vendor_form.is_valid():

                if request.POST.get('save_component') or request.POST.get('save_component_new'):
                    instance = component_form.save(commit=False)
                    instance.created_by = instance.modified_by = request.user
                    instance.date_created = instance.date_modified = datetime.datetime.now()
                
                if request.POST.get('save_costumer') or request.POST.get('save_costumer_new'):
                    instance = costumer_form.save(commit=False)
                    instance.created_by = instance.modified_by = request.user
                    instance.date_created = instance.date_modified = datetime.datetime.now()
                
                if request.POST.get('save_group') or request.POST.get('save_group_new'):
                    instance = group_form.save(commit=False)
                    instance.created_by = instance.modified_by = request.user
                    instance.date_created = instance.date_modified = datetime.datetime.now()
                
                if request.POST.get('save_system') or request.POST.get('save_system_new'):
                    instance = system_form.save(commit=False)
                    instance.created_by = instance.modified_by = request.user
                    instance.date_created = instance.date_modified = datetime.datetime.now()
                
                if request.POST.get('save_type') or request.POST.get('save_type_new'):
                    instance = type_form.save(commit=False)
                    instance.created_by = instance.modified_by = request.user
                    instance.date_created = instance.date_modified = datetime.datetime.now()
                
                if request.POST.get('save_subtype') or request.POST.get('save_subtype_new'):
                    instance = subtype_form.save(commit=False)
                    instance.created_by = instance.modified_by = request.user
                    instance.date_created = instance.date_modified = datetime.datetime.now()
                
                if request.POST.get('save_vendor') or request.POST.get('save_vendor_new'):
                    instance = vendor_form.save(commit=False)
                    instance.created_by = instance.modified_by = request.user
                    instance.date_created = instance.date_modified = datetime.datetime.now()
                
                if request.POST.get('save_allocation') or request.POST.get('save_allocation_new'):
                    instance = form.save(commit=False)
                    instance.modified_by = request.user
                    instance.slug = slugify('{} - {}'.format(instance.allocation_no, instance.component))
                    instance.date_modified = datetime.datetime.now()
                    
                    try:
                        qrcode = create_qrcode(request, instance)
                        instance.qrcode = qrcode
                    except Exception as e:
                        print(f'Error: {e}')
            
                    messages.success(request, _("Allocation created successfully!"))

                instance = instance.save()
                    
                if request.POST.get('save_allocation'):
                    return redirect('asset_app:allocation_list')
                else:
                    return redirect('asset_app:allocation_update', slug=slug)
            else:
                for error in form.errors.values():
                    messages.error(request, error)
                return redirect('asset_app:allocation_update', slug=slug)

        except Exception as e:
            messages.error(request, e)
            return redirect('asset_app:allocation_update', slug=slug)
    
    context = {'form': form, 'component_form': component_form,'costumer_form': costumer_form, 
        'group_form': group_form, 'system_form': system_form, 'type_form': type_form, 
        'subtype_form': subtype_form, 'vendor_form': vendor_form}
    return render(request, 'asset_app/updateviews/allocation_update.html', context)


@login_required
def allocation_delete_view(request):
    if request.is_ajax():
        selected_ids = request.POST['check_box_item_ids']
        selected_ids = json.loads(selected_ids)
        for i, id in enumerate(selected_ids):
            if id != '':
                try:
                    Allocation.objects.filter(id__in=selected_ids).delete()
                except Exception as e:
                    messages.warning(request, _("Not Deleted! {}".format(e)))
                    return redirect('asset_app:allocation_list')
        
        messages.warning(request, _("Allocation delete successfully!"))
        return redirect('asset_app:allocation_list')


@login_required
def allocation_detail_view(request, slug):
    # dictionary for initial data with
    # field names as keys
    allocation = get_object_or_404(Allocation, slug=slug)

    context ={}
    # add the dictionary during initialization
    context["data"] = allocation    
    return render(request, "asset_app/detailviews/allocation_detail_view.html", context)


########################## WorkOrder ##########################
class WorkOrderListView(LoginRequiredMixin, ListView):
    model = WorkOrder
    template_name = 'asset_app/listviews/workorder_list_view.html'


@login_required
def workorder_create_view(request):
    if request.method == 'POST':
        form = WorkOrderForm(request.POST)

        if form.is_valid():
            instance = form.save(commit=False)
            instance.created_by = request.user
            validate_workorder(request, instance)
            instance = instance.save()
            messages.success(request, _("WorkOrder added successfully!"))

            if request.POST.get('save_workorder'):
                return redirect('asset_app:workorder_list')
            else:
                return redirect('asset_app:workorder_create')
        else:
            print(form.errors)
            for error in form.errors.values():
                messages.error(request, error)
            return redirect('asset_app:workorder_create')
    else:
        form = WorkOrderForm()
        context = {'form': form}
        return render(request, 'asset_app/createviews/workorder_create.html', context)


@login_required
def workorder_update_view(request, slug):
    workorder = get_object_or_404(WorkOrder, slug=slug)
    form = WorkOrderForm(request.POST or None, instance=workorder)
   
    if request.method == 'POST':
    
        if form.is_valid():
            instance = form.save(commit=False)
            validate_workorder(request, instance)
            instance = instance.save()
            messages.success(request, _("WorkOrder updated successfully!"))

            if request.POST.get('save_workorder'):
                return redirect('asset_app:workorder_list')
            else:
                return redirect('asset_app:workorder_create')
        else:
            for error in form.errors.values():
                messages.error(request, error)
            return redirect('asset_app:workorder_update', slug=slug)
       
    context = {'form': form}
    return render(request, 'asset_app/updateviews/workorder_update.html', context)

def validate_workorder(request, instance):
    instance.modified_by = request.user
    instance.slug = instance.order
    instance.date_modified = datetime.datetime.now()

@login_required
def workorder_delete_view(request):
    if request.is_ajax():
        selected_ids = request.POST['check_box_item_ids']
        selected_ids = json.loads(selected_ids)
        for i, id in enumerate(selected_ids):
            if id != '':
                try:
                    WorkOrder.objects.filter(id__in=selected_ids).delete()
                except Exception as e:
                    messages.warning(request, _("Not Deleted! {}".format(e)))
                    return redirect('asset_app:workorder_list')
        
        messages.warning(request, _("WorkOrder delete successfully!"))
        return redirect('asset_app:workorder_list')


@login_required
def workorder_detail_view(request, slug):
    # dictionary for initial data with
    # field names as keys
    workorder = get_object_or_404(WorkOrder, slug=slug)
   
    context = {}
    ramaining_time = workorder.end - datetime.datetime.now()
    # add the dictionary during initialization

    if workorder.end < datetime.datetime.now() and workorder.status in ('Pending', 'InProgress'):
        overdue = True
    else:
        overdue = False

    context["data"] = workorder    
    context["overdue"] = overdue    
    context["ramaining_time"] = ramaining_time    
    return render(request, "asset_app/detailviews/workorder_detail_view.html", context)


def create_qrcode(request, instance):
    media = settings.MEDIA_ROOT

    settings_model = Settings.objects.first()
    email = settings_model.email 
    
    allocation_no = instance.allocation_no
    component = instance.component
    costumer = instance.costumer 
    
    subject = _(f"There is a issue with {component}")
    body = f"""
    Allocation Number.: {allocation_no}\n
    Costumer: {costumer}\n
    We have identified a problem with this component: {allocation_no} - {component}
    """

    print(body)

    _file = f"{instance.slug}" + ".png"
    file = os.path.join(media, _file)

    # Absolute path of the file
    path = os.path.realpath(file)
    
    if os.path.exists(path):
        print('Exists')
    else:
        data = f"mailto: {email}?&subject={subject}&body={body}"
        img = qrcode.make(data)
        img.save(path)

    return _file


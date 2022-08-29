# -*- coding: utf-8 -*-
import datetime
import json

from django.shortcuts import render
from django.contrib import messages #import messages
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.decorators import login_required
from django.template.defaultfilters import slugify
from django.shortcuts import render, redirect, HttpResponseRedirect, get_object_or_404, HttpResponse

from .models import Warehouse
from .forms import WarehouseForm
from isis.views import get_model_name_from_id


# Create your views here.
@login_required
def warehouse_create_view(request):
    if request.method == 'POST':
        form = WarehouseForm(request.POST)
        
        if form.is_valid():
            instance = form.save(commit=False)
            instance.created_by = instance.modified_by = request.user
            instance.date_created = instance.date_modified = datetime.datetime.now()
            warehouse = instance
            parent = request.POST.get('parent')
            
            if parent == "":
                instance.parent = 0
            else:
                instance.parent = parent
            
            instance = instance.save()

            slug = slugify(warehouse.name)
            messages.success(request, _("Warehouse added successfully!"))

            if request.POST.get('save_warehouse'):
                return redirect('warehouse:warehouse_details', slug=slug)
            else:
                return redirect('warehouse:warehouse_create')
        else:
            for error in form.errors.values():
                messages.error(request, error)
            return redirect('warehouse:warehouse_create')
    else:
        form = WarehouseForm()
        context = {'form': form}
        return render(request, 'warehouse/createviews/warehouse_create.html', context)


@login_required
def warehouse_list_view(request):
    warehouse = Warehouse.objects.all()
    context = {}
    context['object_list'] = warehouse

    return render(request, 'warehouse/listviews/warehouse_list.html', context) 


@login_required
def warehouse_update_view(request, slug):
    warehouse = get_object_or_404(Warehouse, slug=slug)
    form = WarehouseForm(request.POST or None, instance=warehouse)
	
    if request.method == 'POST':
        
        if form.is_valid():
            instance = form.save(commit=False)
            instance.modified_by = request.user
            instance.slug = slugify(instance.name)
            instance.date_modified = datetime.datetime.now()

            parent = request.POST.get('parent')
            if parent == "":
                instance.parent = 0
            else:
                instance.parent = parent

                # Since parent returns the product id we need to get the name of the parent product
                parent_name =  get_model_name_from_id(Warehouse, parent)
                
                # If the updated product is same as parent
                if parent_name == warehouse.name:
                    print('Same product')
                    instance.parent = 0

            instance = instance.save()
            messages.success(request, _("Warehouse updated successfully!"))

            if request.POST.get('save_warehouse'):
                return redirect('warehouse:warehouse_list')
            else:
                return redirect('warehouse:warehouse_create')

        else:
            for error in form.errors.values():
                messages.error(request, error)
            return redirect('warehouse:warehouse_update', slug=slug)
       
    context = {'form': form}
    return render(request, 'warehouse/updateviews/warehouse_update.html', context)


@login_required
def warehouse_delete_view(request):
    if request.is_ajax():
        selected_ids = request.POST['ckeck_box_item_ids']
        selected_ids = json.loads(selected_ids)
        for i, id in enumerate(selected_ids):
            if id != '':
                try:
                    Warehouse.objects.filter(id__in=selected_ids).delete()
                except Exception as e:
                    messages.warning(request, _("Not Deleted! {}".format(e)))
                    return redirect('warehouse:warehouse_list')
        
        messages.warning(request, _("Warehouse delete successfully!"))
        return redirect('warehouse:warehouse_list')


@login_required
def warehouse_detail_view(request, slug):
    # dictionary for initial data with
    # field names as keys
    warehouse = get_object_or_404(Warehouse, slug=slug)

    child_warehouses = Warehouse.objects.filter(parent=warehouse.id)
    
    try:
        parent_warehouse = Warehouse.objects.get(id=warehouse.parent)
    except warehouse.DoesNotExist:
        parent_warehouse = _('No parent')

    context ={}
    # add the dictionary during initialization
    context["warehouse"] = warehouse    
    context["child_warehouses"] = child_warehouses    
    context["parent_warehouse"] = parent_warehouse 
    return render(request, "warehouse/detailviews/warehouse_detail_view.html", context)

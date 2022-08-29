# -*- coding: utf-8 -*-
import datetime

from django.shortcuts import render, redirect, HttpResponseRedirect, get_object_or_404, HttpResponse
from django.contrib.auth.decorators import login_required
from django.db.models import Sum, Max

from .models import Stock
from isis.models import Product
from warehouse.models import Warehouse

from .forms import StockSearchForm, WarehouseStockSearchForm


# Create your views here.
@login_required
def stock_movement_view(request):
    

    if request.method == 'POST':
        search_form = WarehouseStockSearchForm(request.POST)
        start_date = request.POST.get('start_date')
        end_date = request.POST.get('end_date')
        warehouse = request.POST.get('warehouse')

        if warehouse == '' or warehouse is None:
            stock = Stock.objects.filter(date_created__gte=start_date, 
            date_created__lte=end_date).order_by('-date_created')
        else:
            stock = Stock.objects.filter(date_created__gte=start_date, 
            date_created__lte=end_date, warehouse=warehouse).order_by('-date_created')
    else:
        search_form = WarehouseStockSearchForm
        
        start_date = datetime.datetime.now() - datetime.timedelta(days=7)
        
        end_date = datetime.datetime.now() + datetime.timedelta(days=1)
        stock = Stock.objects.filter(date_created__gte=start_date, 
        date_created__lte=end_date).order_by('-date_created')

    context = {}
    context['object_list'] = stock
    context['search_form'] = search_form

    return render(request, 'stock/listviews/stock_movement.html', context) 


@login_required
def stock_item_list_view(request, slug):
    product = get_object_or_404(Product, slug=slug)
    stock = Stock.objects.filter(product=product).order_by('-date_created')
    
    context = {}
    context['object_list'] = stock
    context['product'] = product
    
    return render(request, 'stock/listviews/stock_item_list.html', context) 


# Create your views here.
@login_required
def stock_summary_list_view(request):
    
    if request.method == 'POST':
        search_form = WarehouseStockSearchForm(request.POST)

        start_date = str(request.POST.get('start_date')).replace('T', ' ')
        end_date = str(request.POST.get('end_date')).replace('T', ' ')
        warehouse = request.POST.get('warehouse')
    else:
        search_form = WarehouseStockSearchForm()
        start_date = datetime.datetime.now() - datetime.timedelta(days=15)
        end_date = datetime.datetime.now() + datetime.timedelta(days=1)
        search_form.start_date = start_date
        warehouse = ''
        
    if warehouse == '' or warehouse is None:
        sql = """SELECT p.*, (SELECT COALESCE(SUM(s.quantity), 0) AS q FROM stock_stock AS s 
        WHERE s.product_id=p.id AND (s.date_created BETWEEN '{}' AND '{}' )) AS qt FROM isis_product AS p""".format(start_date, end_date)
    
    else:
        sql = """SELECT p.*, (SELECT COALESCE(SUM(s.quantity), 0) AS q FROM stock_stock AS s 
        WHERE s.warehouse_id="{warehouse}" AND s.product_id=p.id 
        AND (s.date_created BETWEEN '{}' AND '{}' )) AS qt 
        FROM isis_product AS p""".format(start_date, end_date, warehouse=warehouse)
    
    print(sql)
    object_list = Product.objects.raw(sql)
    context = {}
    context['object_list'] = object_list
    context['search_form'] = search_form
    
    return render(request, 'stock/listviews/stock_summary_list.html', context)


    
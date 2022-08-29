import datetime
import json
from django.urls import reverse_lazy
from django.views.generic import CreateView, UpdateView, ListView, DetailView
from django.contrib.auth.views import LoginView
from django.contrib.auth import login, authenticate, logout
from django.views.generic import FormView
from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.csrf import csrf_protect
from django.contrib import messages
from django.contrib.auth.hashers import make_password
from django.contrib.auth.mixins import (LoginRequiredMixin,)
from django.core.exceptions import ObjectDoesNotExist, ValidationError
from django.urls import reverse
from django.utils.translation import ugettext_lazy as _
from django.http import HttpResponseRedirect, HttpResponse
from django.template import RequestContext
from django.views.defaults import page_not_found, server_error
from django.contrib.auth.decorators import login_required
from django.utils import timezone


from .models import User
from .forms import UserForm, LoginForm, RegisterForm
from django.conf import settings
from warehouse.models import UserWarehouse, Warehouse


def user_login(request):
    # Redirects user to home if a user is already logged in, and is not anonymous
    if request.user.is_anonymous is not True:
        return redirect('/')

    # Like before, obtain the context for the user's request.
    context = {}
    # If the request is a HTTP POST, try to pull out the relevant information.
    if request.method == 'POST':
        # Gather the email and password provided by the user.
        # This information is obtained from the login form.
        email = request.POST['email']
        password = request.POST['password']
        # Use Django's machinery to attempt to see if the email/password
        # combination is valid - a User object is returned if it is.
        user = authenticate(email=email, password=password)
        # If we have a User object, the details are correct.
        # If None (Python's way of representing the absence of a value), no user
        # with matching credentials was found.
        if user is not None:
            # Is the account active? It could have been disabled.
            if user.is_active:
                # If the account is valid and active, we can log the user in.
                # We'll send the user back to the homepage.
                login(request, user)
                messages.success(request, _("Welcome {}.".format(user.username)))
                return HttpResponseRedirect('/')
            else:
                # An inactive account was used - no logging in!
                messages.error(request, _("Your account is disabled."))
                return HttpResponse(_("Your account is disabled."))
        else:
            # Bad login details were provided. So we can't log the user in.
            print("Invalid login details: {0}, {1}".format(email, password))
            return HttpResponse("Invalid login details supplied.")
            # The request is not a HTTP POST, so display the login form.
            # This scenario would most likely be a HTTP GET.
    else:
        # No context variables to pass to the template system, hence the
        # blank dictionary object...
        form = LoginForm()
        context['form'] = form
        return render(request, 'user/login.html', context=context)


def signup(request):
    if request.user.is_anonymous is not True:
        return redirect('/')

    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            if form.is_valid():
                user = form.save()
                user.username = request.POST.get('username')
                # user.last_login = timezone.now
                user.is_active = 1
                user.set_password(user.password)
                user.save()
                return redirect('users:login')

        else:
            for error in form.errors.values():
                messages.error(request, error)
            return redirect('users:register')
    else:
        form = RegisterForm()
    return render(request, 'user/register.html', {'form': form})

def logout_view(request):
    logout(request)
    return redirect('/')


def get_user_id(email_or_user_name):
    q = User.objects.get(email=email_or_user_name)
    user_id = q.id
    return user_id


def handler404(request, exception, template_name="./internationaldonations/404.html"):
    return page_not_found(request, exception, template_name)


def handler500(request, template_name="./internationaldonations/500.html"):
    return server_error(request, template_name)


@login_required
def user_create_view(request):
    if request.method == 'POST':
        form = UserForm(request.POST, request.FILES)
        
        if form.is_valid():
            instance = form.save(commit=False)
            instance.created_by = instance.modified_by = request.user
            instance.date_created = instance.date_modified = datetime.datetime.now()
            instance.username = request.POST.get('username')
            # user.last_login = timezone.now
            instance.is_active = 1
            instance.set_password(instance.password)
            user = instance
            instance = instance.save()
            
            # Saves the warehouse in warehouse_userwarehouse table
            warehouse = Warehouse.objects.filter(id=int(request.POST.get('warehouse'))).first()
    
            w = UserWarehouse(warehouse=warehouse, user=user)
            w.save()
            
            messages.success(request, _("User added successfully!"))

            if request.POST.get('save_user'):
                return redirect('users:user_details', pk=user.pk)
            else:
                return redirect('users:user_create')
        else:
            print(form.errors)
            for error in form.errors.values():
                messages.error(request, error)
            return redirect('users:user_create')
    else:
        form = UserForm()
        context = {'form': form}
        return render(request, 'user/createviews/user_create.html', context)


@login_required
def user_list_view(request):
    user = User.objects.all()
    context = {}
    context['object_list'] = user

    return render(request, 'user/listviews/user_list.html', context) 


@login_required
def user_update_view(request, pk):
    user = get_object_or_404(User, pk=pk)
    form = UserForm(request.POST or None, request.FILES or None, instance=user)
	
    if request.method == 'POST':

        if form.is_valid():
            instance = form.save(commit=False)
            instance.created_by = instance.modified_by = request.user
            instance.date_created = instance.date_modified = datetime.datetime.now()
            instance.username = request.POST.get('username')
            # user.last_login = timezone.now
            instance.is_active = 1
            instance.set_password(instance.password)
            user = instance
            instance = instance.save()

            # Deletes existing warehouse_userwarehouse data
            UserWarehouse.objects.filter(user=user).delete()

            # Saves the warehouse in warehouse_userwarehouse table
            warehouse = Warehouse.objects.filter(id=int(request.POST.get('warehouse'))).first()
    
            w = UserWarehouse(warehouse=warehouse, user=user)
            w.save()

            messages.success(request, _("User updated successfully!"))

            if request.POST.get('save_user'):
                return redirect('users:user_list')
            else:
                return redirect('users:user_create')

        else:
            for error in form.errors.values():
                messages.error(request, error)
            return redirect('users:user_update', pk=pk)

    context = {'form': form}
    return render(request, 'user/updateviews/user_update.html', context)


@login_required
def user_delete_view(request):
    if request.is_ajax():
        selected_ids = request.POST['check_box_item_ids']
        selected_ids = json.loads(selected_ids)
        for i, id in enumerate(selected_ids):
            if id != '':
                try:
                    User.objects.filter(id__in=selected_ids).delete()
                except Exception as e:
                    messages.warning(request, _("Not Deleted! {}".format(e)))
                    return redirect('users:user_list')
        
        messages.warning(request, _("User delete successfully!"))
        return redirect('users:user_list')

@login_required
def user_detail_view(request, pk):
    # dictionary for initial data with
    # field names as keys
    user = get_object_or_404(User, pk=pk)

    context ={}
    # add the dictionary during initialization
    context["user"] = user    
    return render(request, "user/detailviews/user_detail_view.html", context)


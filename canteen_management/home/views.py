from functools import wraps

from django.core.exceptions import ValidationError
from django.db import IntegrityError
from django.shortcuts import get_object_or_404, render,redirect
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from accounts.models import CustomUser
from inventory.models import Inventory
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout


# Create your views here.


def admin_required(view_func):
    @wraps(view_func)
    @login_required(login_url='/login/')
    def _wrapped_view(request, *args, **kwargs):
        user = request.user
        if user.is_canteen_admin:
            return view_func(request, *args, **kwargs)

        messages.error(request, 'You do not have permission to access the admin dashboard.')
        return redirect('/menu/')

    return _wrapped_view

def index_page(request):
    return render(request, 'index.html')


def login_page(request):
    if request.method == 'POST':
        username = request.POST.get('username').strip()
        password = request.POST.get('password').strip()

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)

            # Admin / Staff redirect
            if user.is_canteen_admin:
                return redirect('/admin_page/')

            # Normal user redirect
            return redirect('/menu/')
        else:
            messages.error(request, 'Invalid username or password')

    return render(request, 'login.html')


def register_page(request):
    if request.method == 'POST':
        user_code = (request.POST.get('user_code') or '').strip()
        username = (request.POST.get('username') or '').strip()
        password = request.POST.get('password') or ''
        role = (request.POST.get('role') or '').strip()

        if not CustomUser.is_valid_user_code(user_code):
            messages.error(request, 'UserCode must be exactly 5 numeric characters')
            return redirect('/register/')

        if CustomUser.objects.filter(username=username).exists():
            messages.error(request, 'Username already exists')
            return redirect('/register/')

        if CustomUser.objects.filter(user_code=user_code).exists():
            messages.error(request, 'UserCode already exists')
            return redirect('/register/')

        if role not in CustomUser.registration_roles():
            messages.error(request, 'Invalid role selected')
            return redirect('/register/')

        try:
            CustomUser.objects.create_user(
                username=username,
                password=password,
                role=role,
                user_code=user_code,
            )
        except (IntegrityError, ValidationError, ValueError):
            messages.error(request, 'Unable to register user with the provided details')
            return redirect('/register/')

        return redirect('/login/')
    return render(request, 'register.html')



def logout_view(request):
    logout(request)
    return render(request, 'index.html')

@admin_required
def admin_page(request):
    if request.method == 'POST':
        item_name = request.POST.get('item_name')
        category = request.POST.get('category')
        price = request.POST.get('price')
        quantity = request.POST.get('quantity')
        food_image = request.FILES.get('food_image')

        Inventory.objects.create(item_name=item_name, 
                                category=category,
                                price=price,
                                quantity=quantity,
                                food_image=food_image)
        return redirect('/admin_page/')
    queryset = Inventory.objects.all()
    context = {'inventory': queryset}

    messages.success(request, 'Item added successfully!')
       
    return render(request, 'admin.html', context)

@admin_required
def admin_update_item(request, item_id):
    item = get_object_or_404(Inventory, id=item_id)
    if request.method == 'POST':
        item.item_name = request.POST.get('item_name')
        item.category = request.POST.get('category')
        item.price = request.POST.get('price')
        item.quantity = request.POST.get('quantity')
        if request.FILES.get('food_image'):
            item.food_image = request.FILES.get('food_image')
        item.is_available = request.POST.get('is_available') is not None
        item.save()
        messages.success(request, 'Item updated successfully!')
        return redirect('/admin_page/')
    context = {'item': item}
    return render(request, 'update_admin.html', context)



@admin_required
@require_POST
def admin_delete_item(request, item_id):
    item = get_object_or_404(Inventory, id=item_id)
    item.delete()
    messages.info(request, 'Item deleted successfully!')

    return redirect('/admin_page/')

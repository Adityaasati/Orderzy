from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from accounts.forms import UserProfileForm, UserInfoForm
from accounts.models import UserProfile
from django.contrib import messages
from django.utils import timezone
from datetime import datetime, timedelta
from orders.models import Order,OrderedFood
import simplejson as json
from orders.models import PendingOrders


@login_required(login_url='login')
def cprofile(request):
    profile = get_object_or_404(UserProfile, user=request.user)
    if request.method == 'POST':
        profile_form = UserProfileForm(request.POST, request.FILES, instance=profile)
        user_form = UserInfoForm(request.POST, instance=request.user)
        if profile_form.is_valid() and user_form.is_valid():
            profile_form.save()
            user_form.save()
            messages.success(request, 'Profile Updated')
            return redirect('cprofile')
        else:
            print(profile_form.errors)
            print(user_form.errors)
    else:
        profile_form = UserProfileForm(instance=profile)
        user_form = UserInfoForm(instance=request.user)
    
    context = {
        'profile_form' : profile_form,
        'user_form' : user_form,
        'profile':profile,
    }
    return render(request, 'customers/cprofile.html', context)

@login_required(login_url='login')
def my_orders(request):
    orders = Order.objects.filter(user=request.user, is_ordered=True).order_by('-created_at')
    
    context = {
        'orders':orders,
    }
    return render(request, 'customers/my_orders.html',context)

@login_required(login_url='login')
def order_detail(request, order_number):
    try:
        order = Order.objects.get(order_number=order_number, is_ordered = True)
    except:
        return redirect('customer')
    ordered_food = OrderedFood.objects.filter(order=order)
    subtotal = 0
    ordered_food_details = []
        
    for item in ordered_food:
        subtotal+=(item.price * item.quantity)
        item_sum_price = item.price * item.quantity
        subtotal += item_sum_price
        image_url = item.fooditem.image.url if item.fooditem.image else '/static/default_image.png'

        ordered_food_details.append({
                'fooditem': item.fooditem.food_title,
                'quantity': item.quantity,
                'price': item.price,
                'item_sum_price': item_sum_price,
                'image_url': image_url,
                'restaurant_slug': item.fooditem.restaurant.restaurant_slug,
                'restaurant_name': item.fooditem.restaurant.restaurant_name,
            })
            
            
    try:
        service_charge_data = json.loads(order.service_charge_data)
    except  (json.JSONDecodeError, TypeError):
        service_charge_data = {}
    context = {
            'order':order,
            'ordered_food_details':ordered_food_details,
            'subtotal':subtotal,
            'service_charge_data':service_charge_data
        }

    
    return render (request, 'customers/order_detail.html',context)



@login_required(login_url='login')
def order_cancel(request, order_number):
    order = get_object_or_404(Order, order_number=order_number, is_ordered=True)

    cutoff_time = (order.created_at + timedelta(hours=order.pre_order_time)) - timedelta(minutes=10)
    if timezone.now() > cutoff_time:
        messages.warning(request,"Order cancellation is only allowed up to 10 minutes before the scheduled time.")
        return redirect('customer_my_orders')

    if order.status == "Cancelled":
        messages.warning(request, "This order has already been cancelled.")
        return redirect('customer_my_orders')
    order.status = "Cancelled"    
    order.save()
    try:
            pending_order = PendingOrders.objects.get(po_order_number=order.order_number)
            pending_order.po_status = 'Cancelled'
            pending_order.save()
    except PendingOrders.DoesNotExist:
            # Handle the case where there is no related PendingOrder
            print("No PendingOrder found for this order.")
    messages.success(request, "Your order has been successfully cancelled.")

    return redirect('customer_my_orders')  

@login_required(login_url='login')
def pre_order_time_change(request, order_number):
    order = get_object_or_404(Order, order_number=order_number, is_ordered=True)
    if request.method == 'POST':
        changed_time = request.POST.get('pre_order_time')
        
        try:
            changed_time = float(changed_time)
        except ValueError:
            messages.error(request, "Invalid time format. Please enter a valid number.")
            return redirect('customer_my_orders')

        cutoff_time = (order.created_at + timedelta(minutes=order.pre_order_time)) - timedelta(minutes=15)
        if timezone.now() > cutoff_time:
            messages.warning(request, "Order time change is only allowed up to 15 minutes before the scheduled time.")
            return redirect('customer_my_orders')
        
        order.pre_order_time = changed_time
        order.save()
        
        try:
            pending_order = PendingOrders.objects.get(po_order_number=order.order_number)
            pending_order.po_pre_order_time = changed_time
            pending_order.save()
        except PendingOrders.DoesNotExist:
            print("No PendingOrder found for this order.")

        messages.success(request, "Your pre-order time has been successfully updated.")
        return redirect('customer_my_orders')

    return render(request, 'customers/edit_pre_order_time.html', {'order': order})

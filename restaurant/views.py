from django.shortcuts import render,get_object_or_404, redirect
from.forms import RestaurantForm,OpeningHourForm, SeatingPlanForm
from accounts.forms import UserProfileForm
from accounts.models import UserProfile
from .models import Restaurant,OpeningHour, SeatingPlan
from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from accounts.views import check_role_restaurant
from menu.models import *
from django.db.models import Q
from menu.forms import CategoryForm, FoodItemForm
from django.template.defaultfilters import slugify
from django.http import HttpResponse, JsonResponse
from django.db import IntegrityError
from orders.models import Order,OrderedFood
from orders.models import PendingOrders
import json
from django.shortcuts import render



# Create your views here.



def get_restaurant(request):
    restaurant = Restaurant.objects.get(user = request.user)
    return restaurant


@login_required(login_url='login')
@user_passes_test(check_role_restaurant)
def rprofile(request):
    profile = get_object_or_404(UserProfile,user=request.user)
    restaurant = get_object_or_404(Restaurant,user=request.user)

    if request.method=='POST':
        profile_form = UserProfileForm(request.POST, request.FILES, instance=profile)
        restaurant_form = RestaurantForm(request.POST, request.FILES, instance=restaurant)
        if profile_form.is_valid() and restaurant_form.is_valid():
            profile_form.save()
            restaurant.save()
            messages.success(request, 'Settings Updated')
            return redirect ('rprofile')
        else:
            messages.error(request, 'Please correct the errors below.')
            print(profile_form.errors)
            print(restaurant_form.errors)
    else:
        
        profile_form = UserProfileForm(instance=profile)
        restaurant_form = RestaurantForm(instance=restaurant)
    
    context = {
        'profile_form':profile_form,
        'restaurant_form' : restaurant_form,
        'profile' : profile
    }
    return render(request, 'restaurant/rprofile.html', context)

@login_required(login_url='login')
@user_passes_test(check_role_restaurant)
def menu_builder(request):
    restaurant = get_restaurant(request)
    categories = Category.objects.filter(restaurant=restaurant).order_by('created_at')
    context = {
        'categories' : categories,
    }
    return render (request, 'restaurant/menu_builder.html', context)


@login_required(login_url='login')
@user_passes_test(check_role_restaurant)
def fooditems_by_category(request,pk=None):
    restaurant = get_restaurant(request)
    category = get_object_or_404(Category, pk=pk)
    fooditems = FoodItem.objects.filter(restaurant=restaurant, category = category)
    context = {
        'fooditems':fooditems,
        'category':category
    }
    return render (request, 'restaurant/fooditems_by_category.html',context)



@login_required(login_url='login')
@user_passes_test(check_role_restaurant)
def add_category(request):
    if request.method == 'POST':
        form = CategoryForm(request.POST)
        if form.is_valid():
            category_name = form.cleaned_data['category_name']
            category = form.save(commit=False)
            category.restaurant = get_restaurant(request)
            
            category.save()
            category.slug=slugify(category_name)+'-'+str(category.id)
            category.save()
            messages.success(request,'Category added successfully!')
            return redirect('menu_builder')
        else:
            print(form.errors)
    else:
        form = CategoryForm()
    context = {
        'form':form,
    }
    return render(request, 'restaurant/add_category.html',context)



@login_required(login_url='login')
@user_passes_test(check_role_restaurant)
def edit_category(request,pk=None):
    category = get_object_or_404(Category, pk=pk)
    if request.method == 'POST':
        form = CategoryForm(request.POST, instance=category)
        if form.is_valid():
            category_name = form.cleaned_data['category_name']
            category = form.save(commit=False)
            category.restaurant = get_restaurant(request)
            category.slug=slugify(category_name)
            form.save()
            messages.success(request,'Category added successfully!')
            return redirect('menu_builder')
        else:
            print(form.errors)
    else:
        form = CategoryForm( instance=category)
    context = {
        'form':form,
        'category':category
    }
    return render(request, 'restaurant/edit_category.html', context)
    
 

@login_required(login_url='login')
@user_passes_test(check_role_restaurant)   
def delete_category(request, pk=None):
    category = get_object_or_404(Category, pk=pk)
    category.delete()
    messages.success(request, 'Category Deleted Successfully!')
    return redirect('menu_builder')
    


@login_required(login_url='login')
@user_passes_test(check_role_restaurant)   
def add_food(request):
    if request.method == 'POST':
        form = FoodItemForm(request.POST, request.FILES)
        if form.is_valid():
            foodtitle = form.cleaned_data['food_title']
            food = form.save(commit=False)
            food.restaurant = get_restaurant(request)
            food.save()
            food.slug=slugify(foodtitle)+'-'+str(food.id)
            food.save()
            messages.success(request,'food added successfully!')
            return redirect('fooditems_by_category', food.category.id)
        else:
            print(form.errors)
    else:
        form = FoodItemForm()
        form.fields['category'].queryset = Category.objects.filter(restaurant = get_restaurant(request))
    context = {
        'form':form
    }
    return render(request, 'restaurant/add_food.html',context)
    


@login_required(login_url='login')
@user_passes_test(check_role_restaurant)
def edit_food(request,pk=None):
    food = get_object_or_404(FoodItem, pk=pk)
    if request.method == 'POST':
        form = FoodItemForm(request.POST,request.FILES, instance=food)
        if form.is_valid():
            foodtitle = form.cleaned_data['food_title']
            food = form.save(commit=False)
            food.restaurant = get_restaurant(request)
            food.slug=slugify(foodtitle)
            form.save()
            messages.success(request,'Food Item added successfully!')
            return redirect('fooditems_by_category', food.category.id)
        else:
            print(form.errors)
    else:
        form = FoodItemForm( instance=food)
        form.fields['category'].queryset = Category.objects.filter(restaurant = get_restaurant(request))
        
    context = {
        'form':form,
        'food':food,
    }
    return render(request, 'restaurant/edit_food.html', context)
    
 
@login_required(login_url='login')
@user_passes_test(check_role_restaurant)   
def delete_food(request, pk=None):
    food = get_object_or_404(FoodItem, pk=pk)
    food.delete()
    messages.success(request, 'Food Item Deleted Successfully!')
    return redirect('fooditems_by_category', food.category.id)


def opening_hours(request):
    opening_hours = OpeningHour.objects.filter(restaurant = get_restaurant(request))
    form = OpeningHourForm()
    context = {
        'form':form,
        'opening_hours':opening_hours,
    }
    return render (request, 'restaurant/opening_hours.html',context)

def add_opening_hours(request):
    if request.user.is_authenticated:
        if request.headers.get('x-requested-with') == 'XMLHttpRequest' and request.method  =='POST':
            day = request.POST.get('day')
            from_hour = request.POST.get('from_hour')
            to_hour = request.POST.get('to_hour')
            is_closed = request.POST.get('is_closed')
            try:
                hour = OpeningHour.objects.create(restaurant = get_restaurant(request), day=day, from_hour=from_hour, to_hour=to_hour, is_closed=is_closed)
                if hour:
                    day = OpeningHour.objects.get(id=hour.id)
                    if day.is_closed:
                        response = {'status':'success' , 'id': hour.id, 'day':day.get_day_display(), 'is_closed':'Closed'}
                    else:
                        response = {'status':'success' , 'id': hour.id, 'day':day.get_day_display(), 'from_hour':hour.from_hour, 'to_hour':to_hour}
                        
                
                return JsonResponse(response)
            except IntegrityError as e:
                response = {'status':'failed', 'message':from_hour+ '-' + to_hour + 'already exists for this day!'}
                return JsonResponse(response)
                
        else: 
            return HttpResponse('Add opening Hours')

def remove_opening_hours(request, pk=None):
    if request.user.is_authenticated:
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            hour = get_object_or_404(OpeningHour,pk=pk)
            hour.delete()
            return JsonResponse({'status':'success','id':pk})
        else:
            
            return HttpResponse('This action can only be performed via an AJAX request.', status=400)
    else:
        return HttpResponse('Unauthorized', status=401)   

def order_detail(request, order_number):
    try:
        order = Order.objects.get(order_number=order_number, is_ordered=True)
        ordered_food = OrderedFood.objects.filter(order=order, fooditem__restaurant=get_restaurant(request))
        ordered_food_details = []
        for item in ordered_food:
            item_sum_price = item.price * item.quantity
            ordered_food_details.append({
                'fooditem': item.fooditem.food_title,
                'quantity': item.quantity,
                'price': item.price,
                'item_sum_price': item_sum_price,
                'image_url': item.fooditem.image.url,
                'restaurant_slug': item.fooditem.restaurant.restaurant_slug,
                'restaurant_name': item.fooditem.restaurant.restaurant_name,
            })
        
        
        context = {
            'order':order,
            'ordered_food_details':ordered_food_details,
            'subtotal':order.get_total_by_restaurant()['subtotal'],
            'service_charge_data':order.get_total_by_restaurant()['service_charge_dict'],
            'grand_total':order.get_total_by_restaurant()['grand_total'],
            
        }
        print(order.total_data,"Ye order total data hai")
    
    except:
        return redirect('restaurant')
    return render(request, 'restaurant/order_detail.html',context)



def my_orders(request):
    restaurant = Restaurant.objects.get(user=request.user)
    orders = Order.objects.filter( restaurants__in=[restaurant.id],is_ordered=True).order_by('-created_at')
    print("order",orders)

    context = {
        'orders':orders,
    }
    
    return render(request, 'restaurant/my_orders.html',context)


@login_required(login_url='login')
@user_passes_test(check_role_restaurant)  
def pending_orders(request):
    restaurant = Restaurant.objects.get(user=request.user)
    pending_orders = PendingOrders.objects.filter( po_restaurant_id=restaurant.id,po_is_ordered=True).order_by('-po_created_at')
    
    context = {

        'pending_orders':pending_orders,   
    }

    return render(request, 'restaurant/pending__orders.html', context)

def accept_po(request, id):
    if request.method == 'POST':
        pending_order = get_object_or_404(PendingOrders, pk=id)
        pending_order.po_status = 'Accepted'
        pending_order.save()
        
        
    return redirect('restaurant_pending_orders')

        
def ready_po(request, id):
    restaurant = Restaurant.objects.get(user=request.user)
    
    seating_plan, created = SeatingPlan.objects.get_or_create(
        restaurant=restaurant,
        defaults={'seating_plan_available': False}  # Default values if creating a new SeatingPlan
    )
    
    if not seating_plan.seating_plan_available:
        if request.method == 'POST':
            pending_order = get_object_or_404(PendingOrders, pk=id)
            pending_order.po_status = 'Ready'
            pending_order.save()
            
            return redirect('restaurant_pending_orders')

    if request.method == 'POST':
        pending_order = get_object_or_404(PendingOrders, pk=id)
        pending_order.po_status = 'Ready'
        pending_order.save()

        if pending_order.po_num_of_people > 0 & pending_order.po_num_of_people <=2:
            seating_plan.tables_for_two-=1
            seating_plan.save() 
        elif pending_order.po_num_of_people >2 & pending_order.po_num_of_people <=4:
            seating_plan.tables_for_four-=1
            seating_plan.save() 
        elif pending_order.po_num_of_people >4 & pending_order.po_num_of_people <=6:
            seating_plan.tables_for_six-=1
            seating_plan.save() 
            
        return redirect('restaurant_pending_orders')
    

    
def delete_po(request, id):
    if request.method == 'POST':
        pending_order = get_object_or_404(PendingOrders, pk=id)
        try:
            pending_order.delete()
            return redirect('restaurant_pending_orders')
        except Exception as e:
            print("Error is", e)
            return redirect('restaurant_pending_orders')
       
        
        
        
def completed_po(request, id):
    restaurant = Restaurant.objects.get(user=request.user)
    seating_plan, created = SeatingPlan.objects.get_or_create(
        restaurant=restaurant,
        defaults={'seating_plan_available': False}  # Default values if creating a new SeatingPlan
    )
    
    if not seating_plan.seating_plan_available:
        if request.method == 'POST':
            pending_order = get_object_or_404(PendingOrders, pk=id)
            pending_order.po_status = 'Completed'
            pending_order.save()
            return redirect('restaurant_pending_orders')
            
        
    if request.method == 'POST':
        pending_order = get_object_or_404(PendingOrders, pk=id)
        pending_order.po_status = 'Completed'
        pending_order.save()
        if pending_order.po_num_of_people > 0 & pending_order.po_num_of_people <=2:
            seating_plan.tables_for_two+=1
            seating_plan.save() 
        elif pending_order.po_num_of_people >2 & pending_order.po_num_of_people <=4:
            seating_plan.tables_for_four+=1
            seating_plan.save() 
        elif pending_order.po_num_of_people >4 & pending_order.po_num_of_people <=6:
            seating_plan.tables_for_six+=1
            seating_plan.save() 
    return redirect('restaurant_pending_orders')

    
        



def seating_plan_view(request):
    restaurant = get_object_or_404(Restaurant, user=request.user)

    seating_plan, created = SeatingPlan.objects.get_or_create(restaurant=restaurant)

    if request.method == 'POST':
        form = SeatingPlanForm(request.POST, instance=seating_plan)
        if form.is_valid():
            form.save()
            context = {
                'form': form,
                'seating_plan': seating_plan,
                'success': True,
            }
            return render(request, 'restaurant/seating_plan.html', context)
    else:
        form = SeatingPlanForm(instance=seating_plan)
        context = {
            'form': form,
            'seating_plan': seating_plan,
        }
    return render(request, 'restaurant/seating_plan.html', context)

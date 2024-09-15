from django.shortcuts import render, get_object_or_404, redirect
from restaurant.models import Restaurant,OpeningHour,SeatingPlan,FoodHub
from menu.models import Category, FoodItem
from django.db.models import Prefetch
from django.http import JsonResponse
from .models import Cart
from .context_processors import get_cart_counter, get_cart_amounts
from django.contrib.auth.decorators import login_required
from datetime import date, datetime
from orders.forms import OrderForm
from accounts.models import UserProfile
from django.db.models import Q
from django.contrib.gis.geos import GEOSGeometry
from django.contrib.gis.measure import D
from django.contrib.gis.db.models.functions import Distance
from django.contrib import messages


def marketplace(request):
    restaurants = Restaurant.objects.filter(is_approved=True, user__is_active=True)
    restaurant_count = restaurants.count()
    context = {
        'restaurants':restaurants,
        'restaurant_count':restaurant_count,
    }
    return render(request, 'marketplace/listings.html', context)

def restaurant_detail(request, restaurant_slug):
    restaurant = get_object_or_404(Restaurant, restaurant_slug=restaurant_slug)
    try:
        seating_plan = SeatingPlan.objects.get(restaurant=restaurant)
        if seating_plan.tables_for_two == 0 & seating_plan.tables_for_four == 0 & seating_plan.tables_for_six ==0:
            seating_available = 0 
        else:
            seating_available = "None"
    except:
        seating_available = "None"
        print("HH")
        pass
    
    categories = Category.objects.filter(restaurant=restaurant).prefetch_related(
        Prefetch(
            'fooditems',
            queryset = FoodItem.objects.filter(is_available=True)
        )
    )
    
    opening_hours = OpeningHour.objects.filter(restaurant=restaurant).order_by('day','-from_hour')
    
    today_date= date.today()
    today = today_date.isoweekday()
    current_opening_hours = OpeningHour.objects.filter(restaurant=restaurant, day=today)

    if request.user.is_authenticated:
        cart_items = Cart.objects.filter(user=request.user)
    else:
        cart_items=None
        
    try:
        cart_item_quantities = {}
        for item in cart_items:
            cart_item_quantities[item.fooditem.id] = item.quantity
        
        context = {
        'restaurant_slug':restaurant_slug,
        'categories':categories,
        'restaurant':restaurant,
        'cart_items':cart_items,
        'opening_hours':opening_hours,
        'current_opening_hours':current_opening_hours,
        'cart_item_quantities':cart_item_quantities,
        'seating_available':seating_available,
        }
        
    except:
        context = {
        'restaurant_slug':restaurant_slug,
        'categories':categories,
        'restaurant':restaurant,
        'opening_hours':opening_hours,
        'current_opening_hours':current_opening_hours,}
    return render(request, 'marketplace/restaurant__detail.html',context)
    


def add_to_cart(request, food_id):
    if request.user.is_authenticated:
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            try:
                fooditem = FoodItem.objects.get(id=food_id)
                try:
                    check_cart = Cart.objects.get(user = request.user,fooditem=fooditem )
                    check_cart.quantity += 1
                    check_cart.save()
                    return JsonResponse({'status':'Success','message':'Increased cart quantity','cart_counter':get_cart_counter(request), 'qty':check_cart.quantity,'cart_amount':get_cart_amounts(request)})
                except:
                    check_cart = Cart.objects.create(user=request.user, fooditem=fooditem, quantity=1)
                    return JsonResponse({'status':'Success','message':'Added the food to cart','cart_counter':get_cart_counter(request), 'qty':check_cart.quantity,'cart_amount':get_cart_amounts(request)})
                    
                    
            except:
                return JsonResponse({'status':'Failed','message':'This food item does not exist'})
                
        else:
            return JsonResponse({'status':'Failed','message':'Invalid Request'})
            
    else:
        
        return JsonResponse({'status':'login_required','message':'Please Login to continue'})
    
    
def decrease_cart(request,food_id):
    if request.user.is_authenticated:
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            try:
                fooditem = FoodItem.objects.get(id=food_id)
                try:
                    check_cart = Cart.objects.get(user = request.user,fooditem=fooditem )
                    if check_cart.quantity>1:
                        
                        check_cart.quantity -= 1
                        check_cart.save()
                    else:
                        check_cart.delete()
                        check_cart.quantity = 0
                        
                    return JsonResponse({'status':'Success','cart_counter':get_cart_counter(request), 'qty':check_cart.quantity,'cart_amount':get_cart_amounts(request)})
                except:
                    return JsonResponse({'status':'Failed','message':'You do not have this item in your cart!'})
                    
                    
            except:
                return JsonResponse({'status':'Failed','message':'This food item does not exist'})
                
        else:
            return JsonResponse({'status':'Failed','message':'Invalid Request'})
            
    else:
        
        return JsonResponse({'status':'login_required','message':'Please Login to continue'})
   
@login_required(login_url='login')
def cart(request):
    cart_items = Cart.objects.filter(user=request.user).order_by('created_at')
    context={
        'cart_items':cart_items,
    }
    return render (request, 'marketplace/cart.html',context)

def delete_cart(request, cart_id):
    if request.user.is_authenticated:
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            try:
                cart_item = Cart.objects.get(user=request.user, id=cart_id)
                if cart_item:
                    cart_item.delete()
                    return JsonResponse({'status':'Success','message':'Cart Item has been deleted!','cart_counter':get_cart_counter(request),'cart_amount':get_cart_amounts(request)})
                    
            except:
                return JsonResponse({'status':'Failed','message':'Cart item does not exist'})
                
                
        else:
            return JsonResponse({'status':'Failed','message':'Invalid Request'})
            
            
def search(request):
    address = request.GET.get('address', '')
    latitude = request.GET.get('lat', '')
    longitude = request.GET.get('lng', '')
    keyword = request.GET.get('keyword', '')
    selected_food_hub = request.GET.get('food_hub', '')

    fetch_restaurants_by_fooditems = FoodItem.objects.filter(food_title__icontains=keyword, is_available=True).values_list('restaurant', flat=True)
    restaurants = Restaurant.objects.filter(
        Q(id__in=fetch_restaurants_by_fooditems) |
        Q(restaurant_name__icontains=keyword, is_approved=True, user__is_active=True)
    )

    if selected_food_hub:
        restaurants = restaurants.filter(food_hub__id=selected_food_hub)

    elif latitude and longitude:
        pnt = GEOSGeometry('POINT(%s %s)' % (longitude, latitude))
        
        # Update restaurant queryset with distance annotation
        restaurants = restaurants.filter(
            user_profile__location__distance_lte=(pnt, D(km=2000))
        ).annotate(distance=Distance("user_profile__location", pnt)).order_by("distance")
        
        # Get nearby food hubs
        nearby_food_hubs = FoodHub.objects.filter(
            location__distance_lte=(pnt, D(km=100))
        ).annotate(distance=Distance("location", pnt)).order_by("distance")
        
        for r in restaurants:
            r.kms = round(r.distance.km, 1)
            
        food_hubs_count = nearby_food_hubs.count()

    else:
        print("Entered in else")
        note = "Sorry for your inconvenience. Currently we do not have your item."
        # messages.warning(request, "Sorry, Currently we do not have your item.")
        print(note)
        
        nearby_food_hubs = 0
        food_hubs_count = 0

    context = {
        'restaurants': restaurants,
        'nearby_food_hubs': nearby_food_hubs,
        'food_hubs_count': food_hubs_count,
        'source_location': address,
        
    }
    
    
    print(context)
    return render(request, 'marketplace/listings.html', context)


@login_required(login_url = 'login')
def checkout(request):
    cart_items = Cart.objects.filter(user=request.user).order_by('created_at')
    cart_count = cart_items.count()
    if cart_count <=0:
        messages.warning(request, 'Currently, your cart is empty.')
        return redirect('marketplace')
    
    user_profile = UserProfile.objects.get(user = request.user)
    default_values = {
        'first_name': request.user.first_name,
        'last_name': request.user.last_name,
        'phone': request.user.phone_number,
        'email':request.user.email,  
    }
    
    cart_items_with_totals = []
    restaurants_in_order = set()
    for item in cart_items:
        total_price = item.fooditem.price * item.quantity
        restaurants_in_order.add(item.fooditem.restaurant.id)
    

        cart_items_with_totals.append({
            'item': item,
            'total_price': total_price,
        })

    num_of_restaurants = len(restaurants_in_order)
    if num_of_restaurants == 1:
        try:
            restaurant_id_ins = restaurants_in_order.pop()
            seating_plan = SeatingPlan.objects.get(restaurant=restaurant_id_ins)
            seating_plan_available = seating_plan.seating_plan_available
            form = OrderForm(initial = default_values, restaurant=restaurant_id_ins, has_seating_plan=seating_plan_available)
            
            
        except:
            seating_plan_available = "False"
            form = OrderForm(initial = default_values)
    else:
        seating_plan_available = "False"
        form = OrderForm(initial = default_values) 

    context = {
        'form':form,
        'cart_items_with_totals':cart_items_with_totals,
        'cart_count':cart_count,
        'num_of_restaurants':num_of_restaurants,
        'seating_plan_available':seating_plan_available,
    }
    return render(request, 'marketplace/checkout.html',context)



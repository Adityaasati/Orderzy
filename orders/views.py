from django.shortcuts import render, redirect, HttpResponse
from django.http import  JsonResponse
from marketplace.models import Cart
from marketplace.context_processors import get_cart_amounts
from .forms import OrderForm
import simplejson as json
from .utils import generate_order_number,order_total_by_restaurant
from .models import Payment,OrderedFood,Order, PendingOrder
from accounts.utils import send_notification
from django.contrib.auth.decorators import login_required
from menu.models import FoodItem
from marketplace.models import Service_Charge
from django.contrib.sites.shortcuts import get_current_site



@login_required(login_url='login')
def place_order(request):
    cart_items = Cart.objects.filter(user=request.user).order_by('created_at')
    cart_count = cart_items.count()
    if cart_count <=0:
        return redirect('marketplace')
    
    restaurants_ids = []
    for i in cart_items:
        if i.fooditem.restaurant.id not in restaurants_ids:
            restaurants_ids.append(i.fooditem.restaurant.id)
    
    get_service_charge = Service_Charge.objects.filter(is_active=True)
    
    subtotal=0 
    total_data = {}
    k={}
    for i in cart_items:
        fooditem = FoodItem.objects.get(pk=i.fooditem.id, restaurant_id__in = restaurants_ids)
        r_id = fooditem.restaurant.id
        if r_id in k:
            subtotal = k[r_id]
            subtotal += (fooditem.price * i.quantity)
            k[r_id] = subtotal
        else:
            subtotal = (fooditem.price * i.quantity)
            k[r_id] = subtotal
        service_charge_dict = {}
        for i in get_service_charge:
            service_charge_type = i.service_charge_type
            service_charge_percentage = i.service_charge_percentage
            service_charge_amount = round((service_charge_percentage * subtotal) / 100, 2)
            service_charge_dict.update({service_charge_type: {str(service_charge_percentage): str(service_charge_amount) }})
           
        total_data.update({fooditem.restaurant.id:{str(subtotal): str(service_charge_dict)}})
    subtotal = get_cart_amounts(request)['subtotal']
    total_charge = get_cart_amounts(request)['service_charge']
    grand_total = get_cart_amounts(request)['grand_total']
    service_charge_data = get_cart_amounts(request)['service_charge_dict']
    

    if request.method == 'POST':
        form = OrderForm(request.POST)
        prd = request.POST.get('pre_order_time')
        
        if form.is_valid():
            order = Order()
            order.first_name = form.cleaned_data['first_name']
            order.last_name = form.cleaned_data['last_name']
            order.phone = form.cleaned_data['phone']
            order.email = form.cleaned_data['email']
            order.user = request.user
            order.total = grand_total
            order.service_charge_data = json.dumps(service_charge_data)
            order.total_data = json.dumps(total_data)
            order.total_charge = total_charge
            order.payment_method = request.POST['payment_method']
            print("order.payment_method ",order.payment_method )
            order.pre_order_time = float(request.POST.get('pre_order_time', 0)) 
            num_of_people = form.cleaned_data.get('num_of_people', 0)
            order.num_of_people = num_of_people if num_of_people is not None else 0
            print("order.pre_order_time",order.pre_order_time)
            order.save()  

            order.order_number = generate_order_number(order.id)
            order.restaurants.add(*restaurants_ids)  
           
            order.save()  

            restaurant_ids = list(set([item.fooditem.restaurant.id for item in cart_items]))
            cart_items_with_totals = []
            for item in cart_items:
                total_price = item.fooditem.price * item.quantity
                cart_items_with_totals.append({
                'item': item,
                'total_price': total_price,
                })

            if len(restaurant_ids) == 1:
                restaurant_id=restaurant_ids[0]
                pending_order_queryset = PendingOrder.objects.filter(po_restaurant_id=restaurant_id).order_by('po_id')

                pending_order = pending_order_queryset.last()
                current_restaurant_order = pending_order.get_restaurant_order_number()
                preparing_restaurant_order = pending_order.preparing_restaurant_order_number()
                away_restaurant_order = (current_restaurant_order - preparing_restaurant_order) + 1
                
                context = {
                        'order':order,
                        'cart_items_with_totals':cart_items_with_totals,
                        'restaurant_ids':restaurant_ids,
                        'current_restaurant_order':current_restaurant_order,
                        'preparing_restaurant_order':preparing_restaurant_order,
                        'away_restaurant_order':away_restaurant_order,
                            }
                
            else:
                context = {
                    'order':order,
                    'cart_items_with_totals':cart_items_with_totals,
                    'restaurant_ids':restaurant_ids,}
                
                
            return render(request, 'orders/place_order.html',context)
                
        else:
            print("form is not valid")
            print("form.errors:", form.errors)
   
    else:
        print("request is not post")        
    return render(request, 'orders/place_order.html')

@login_required(login_url='login')
def payments(request):
    if request.headers.get('x-requested-with') == 'XMLHttpRequest' and request.method == 'POST':
        order_number = request.POST.get('order_number')
        transaction_id = request.POST.get('transaction_id')
        payment_method = request.POST.get('payment_method')
        status = request.POST.get('status')
        order_number = request.POST.get('order_number')
        order = Order.objects.get(user=request.user, order_number=order_number)
        payment = Payment(
            user = request.user,
            transaction_id = transaction_id,
            payment_method = payment_method,
            amount = order.total,
            status = status
            
        )
        payment.save()
        order.payment = payment
        order.is_ordered = True
        order.save()
        
        cart_items = Cart.objects.filter(user=request.user)
        for item in cart_items:
            ordered_food = OrderedFood()
            ordered_food.order = order
            ordered_food.payment=payment
            ordered_food.user= request.user
            ordered_food.fooditem = item.fooditem
            ordered_food.quantity = item.quantity
            ordered_food.price = item.fooditem.price
            ordered_food.amount = item.fooditem.price * item.quantity
            ordered_food.save()
        
        
        mail_subject = 'Thanyou for Ordering with us!'
        mail_template = 'orders/order_confirmation_email.html'
        
        ordered_food = OrderedFood.objects.filter(order=order)
        customer_subtotal = 0
        
        for item in ordered_food:
            customer_subtotal += (item.price * item.quantity )
            
        service_charge_data = json.loads(order.service_charge_data)
        context = {
            'user':request.user,
            'order':order,
            'to_email':order.email,
            'ordered_food':ordered_food,
            'domain': get_current_site(request),
            'customer_subtotal':customer_subtotal,
            'service_charge_data':service_charge_data,
        }
        send_notification(mail_subject, mail_template, context)
        
        mail_subject="You have received a new order!"
        mail_template = "orders/new_order_received.html"
        
        to_emails = []
        for i in cart_items:
            if i.fooditem.restaurant.user.email not in to_emails:
                to_emails.append(i.fooditem.restaurant.user.email)
        
                ordered_food_to_restaurant = OrderedFood.objects.filter(order=order, fooditem__restaurant=i.fooditem.restaurant)
               
                context = {
                    'order':order,
                    'to_email':i.fooditem.restaurant.user.email,
                    'ordered_food_to_restaurant':ordered_food_to_restaurant,
                    'restaurant_subtotal':order_total_by_restaurant(order, i.fooditem.restaurant.id)['subtotal'],
                    'service_charge_data':order_total_by_restaurant(order, i.fooditem.restaurant.id)['service_charge_dict'],
                    'restaurant_grand_total': order_total_by_restaurant(order, i.fooditem.restaurant.id)['grand_total'],
                }

                send_notification(mail_subject, mail_template, context)
        
        response = {
            'order_number':order_number,
            'transaction_id':transaction_id,
        }
        
        return JsonResponse(response)
    return HttpResponse('Payments view')

@login_required(login_url='login')
def order_complete(request):
    order_number = request.GET.get('order_no')
    transaction_id = request.GET.get('trans_id')
    
    if transaction_id == 'RESTAURANTORDER':
        order.is_ordered = True
        order.save()
        
        cart_items = Cart.objects.filter(user=request.user)
        for item in cart_items:
            ordered_food = OrderedFood()
            ordered_food.order = order
            ordered_food.user= request.user
            ordered_food.fooditem = item.fooditem
            ordered_food.quantity = item.quantity
            ordered_food.price = item.fooditem.price
            ordered_food.amount = item.fooditem.price * item.quantity
            ordered_food.save()
    
    try:
        if transaction_id == 'RESTAURANTORDER':
            order = Order.objects.get(order_number=order_number, is_ordered=True)
        else:  
            order = Order.objects.get(order_number=order_number, payment__transaction_id=transaction_id, is_ordered=True)
        ordered_food = OrderedFood.objects.filter(order=order)
        subtotal = 0
        
        for item in ordered_food:
            subtotal+=(item.price * item.quantity)
        service_charge_data = json.loads(order.service_charge_data)

        restaurants_pendings = order.restaurants.all()
        
        for restaurant in restaurants_pendings:
            ordered_food = OrderedFood.objects.filter(
                fooditem__restaurant=restaurant,
                order=order  
            )
           
            subtotal = 0
            for item in ordered_food:
                subtotal += item.price * item.quantity
            
            ordered_food_details = [
                {
                    'fooditem': item.fooditem.food_title,
                    'quantity': item.quantity,
                    'price':item.price,
                    'item_sum_price': item.price * item.quantity,
                    'image_url': item.fooditem.image.url,
                    'restaurant_slug': item.fooditem.restaurant.restaurant_slug,
                    'restaurant_name':item.fooditem.restaurant.restaurant_name,
                } for item in ordered_food
            ]
            
            if order.pre_order_time > 0:
                order_type = "Preorder"
            else:    
                order_type = "Immediate"
            
            pending_order = PendingOrder(
            po_order_number=order.order_number,
            po_is_ordered=order.is_ordered,
            po_created_at=order.created_at,
            po_pre_order_time=order.pre_order_time,
            po_ordered_food_details=ordered_food_details,  
            po_name=order.name,
            po_total=subtotal,
            po_status=order.status,
            po_order_type = order_type,
            po_total_data=order.total_data,
            po_restaurant_id = restaurant.id,
            po_num_of_people = order.num_of_people)

            
            pending_order.save()
            pending_order.po_restaurants.add(restaurant)
            pending_order.save()

        context = {
            'order':order,
            'ordered_food_details':ordered_food_details,
            'subtotal':subtotal,
            'service_charge_data':service_charge_data
        }
        Cart.objects.filter(user=request.user).delete()
        return render(request, 'orders/order_complete.html',context)
        
    except:
        return redirect('home')
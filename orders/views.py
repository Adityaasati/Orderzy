# Standard Library Imports
import json
import uuid
import os

# Third-Party Imports
import requests
import simplejson as json
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.sites.shortcuts import get_current_site
from django.conf import settings
from django.db import transaction
from django.http import JsonResponse, HttpResponse
from django.shortcuts import render, redirect
from django.urls import reverse

# Local Application Imports
from accounts.models import User
from accounts.utils import send_notification
from cashfree_pg.api_client import Cashfree
from cashfree_pg.models.create_order_request import CreateOrderRequest
from cashfree_pg.models.customer_details import CustomerDetails
from cashfree_pg.models.order_meta import OrderMeta
from .forms import OrderForm
from .models import Payment, OrderedFood, Order, PendingOrders
from .utils import DecimalEncoder, generate_order_number, order_total_by_restaurant
from marketplace.context_processors import get_cart_amounts
from marketplace.models import Cart, Service_Charge
from menu.models import FoodItem
import base64
import hashlib
import hmac
from django.contrib.auth import login
import threading
import logging
from hmac import compare_digest
from django.db import transaction
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
from django.core import signing
from django.utils.http import urlencode

logging.basicConfig(level=logging.INFO)  



logger = logging.getLogger(__name__)

cashfree_logger = logging.getLogger('cashfree')



Cashfree.XClientId = settings.CASHFREE_X_CLIENT_ID
Cashfree.XClientSecret = settings.CASHFREE_X_CLIENT_SECRET
x_api_version = settings.X_API_VERSION
if settings.DEBUG == True:
    Cashfree.XEnvironment = Cashfree.SANDBOX
else:
    Cashfree.XEnvironment = Cashfree.PRODUCTION



@login_required(login_url='login')
def place_order(request):
    
    cart_items = Cart.objects.filter(user=request.user).order_by('created_at')
    cart_count = cart_items.count()
    print("request.user.id",request.user.id)
    logger.info("User ID: %s", request.user.id)

    print(request.user,"user")
    
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
            try:
                order.service_charge_data = json.dumps(service_charge_data, cls=DecimalEncoder)
                order.total_data = json.dumps(total_data, cls=DecimalEncoder)
            except TypeError as e:
                print(f"Error serializing data: {e}")
                return JsonResponse({'error': 'Unable to serialize data.'}, status=500)
            
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

            if order.payment_method == "Cash":
                order.is_ordered = True
                order.save()
                cart_items = Cart.objects.filter(user=request.user)
                for item in cart_items:
                    ordered_food = OrderedFood(
                    order=order,
                    payment=None,
                    user=request.user,
                    fooditem=item.fooditem,
                    quantity=item.quantity,
                    price=item.fooditem.price,
                    amount=item.fooditem.price * item.quantity
                    )
                    ordered_food.save()
    
            else:
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
                pending_order_queryset = PendingOrders.objects.filter(po_restaurant_id=restaurant_id).order_by('id')

                pending_order = pending_order_queryset.last()
                if pending_order is not None:
                    current_restaurant_order = pending_order.get_restaurant_order_number()
                    preparing_restaurant_order = pending_order.preparing_restaurant_order_number()
                    away_restaurant_order = (current_restaurant_order - preparing_restaurant_order) + 1
                
                    context = {
                        'user':order.user,
                        'order':order,
                        'cart_items_with_totals':cart_items_with_totals,
                        'restaurant_ids':restaurant_ids,
                        'current_restaurant_order':current_restaurant_order,
                        'preparing_restaurant_order':preparing_restaurant_order,
                        'away_restaurant_order':away_restaurant_order,
                            }
                else:
                    context = {
                    'user':order.user,
                    'order':order,
                    'cart_items_with_totals':cart_items_with_totals,
                    'restaurant_ids':restaurant_ids,}
            else:
                context = {
                    'user':order.user,
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




def fetch_order(order_number, transaction_id=None):
    """
    Fetches the Order based on order_number.
    
    """
    return Order.objects.select_related('user').prefetch_related('orderedfood_set__fooditem__restaurant').get(
        order_number=order_number,
        is_ordered=True
    )



def create_pending_order(order, restaurant):
    """
    Creates a PendingOrders instance for a given order and restaurant.
    """
    logging.info("Entered create_pending_order for order: %s, restaurant: %s", order.order_number, restaurant.restaurant_name)
    
    current_ordered_food_details = []
    try:
        ordered_food = OrderedFood.objects.filter(
            fooditem__restaurant=restaurant,
            order=order
        ).select_related('fooditem__restaurant')
        logging.info("Fetched ordered_food for restaurant: %s, count: %d", restaurant.restaurant_name, ordered_food.count())

        if not ordered_food.exists():
            logging.warning("No ordered food items found for order: %s, restaurant: %s", order.order_number, restaurant.restaurant_name)
            return 0, []

        subtotal = sum(item.price * item.quantity for item in ordered_food)
        logging.info("Subtotal calculated for restaurant: %s is %s", restaurant.restaurant_name, subtotal)

        current_ordered_food_details.extend([
            {
                'fooditem': item.fooditem.food_title,
                'quantity': item.quantity,
                'price': item.price,
                'item_sum_price': item.price * item.quantity,
                'image_url': item.fooditem.image.url if item.fooditem.image else '/static/default_image.png',
                'restaurant_slug': item.fooditem.restaurant.restaurant_slug,
                'restaurant_name': item.fooditem.restaurant.restaurant_name,
            } for item in ordered_food
        ])
        logging.info("current_ordered_food_details created for order: %s, count: %d", order.order_number, len(current_ordered_food_details))

        order_type = "Preorder" if order.pre_order_time > 0 else "Immediate"

        pending_order = PendingOrders(
            po_order_number=order.order_number,
            po_is_ordered=order.is_ordered,
            po_created_at=order.created_at,
            po_pre_order_time=order.pre_order_time,
            po_ordered_food_details=current_ordered_food_details, 
            po_name=order.name,
            po_total=subtotal,
            po_status=order.status,
            po_order_type=order_type,
            po_total_data=order.total_data,
            po_restaurant_id=restaurant.id,
            po_num_of_people=order.num_of_people,
            original_order=order  # Link to the original order
        )
        pending_order.save()
        logging.info("Pending order saved successfully for order number: %s, restaurant: %s", order.order_number, restaurant.restaurant_name)

        pending_order.po_restaurants.add(restaurant)
        logging.info("Restaurant added to pending order's po_restaurants for order number: %s", order.order_number)

        return subtotal, current_ordered_food_details

    except Exception as e:
        logging.error("Error in create_pending_order for order number: %s, restaurant: %s. Error: %s", order.order_number, restaurant.restaurant_name, str(e))
        return 0, []

   

@csrf_exempt
def create_order_api(request):
    logger.info("Received request with method in create order: %s", request.method)

    if request.method == 'POST':
        try:
            print(request.body) 
            data = json.loads(request.body)
            logger.debug("Request body: %s", request.body)

            print("Data loaded:", data)
            logger.debug("Data loaded: %s", data)

            

            customer_id = data['customer_details']['customer_id']
            customer_phone = data['customer_details']['customer_phone']
            order_id = data['order_id']
            order_amount = float(data['order_amount'])
            customer_details = CustomerDetails(customer_id=customer_id,
                                               customer_phone=customer_phone)
            logger.debug("Customer ID: %s", customer_id)
            logger.debug("Order ID: %s", order_id)
        
            
            auth_token = generate_auth_token(request.user)
            print(auth_token,"auth_token")
            logger.debug("Auth Token: %s", auth_token)
            
            
            BASE_URL = 'https://orderzy.in' if not settings.DEBUG else 'https://c797-2409-40c4-276-ab4d-8ca3-d050-65e8-f7b7.ngrok-free.app'
            logger.debug("BASE_URL: %s", BASE_URL)
            print("BASE URL ",BASE_URL)

            # Return and Notify URLs
            return_url = f"{BASE_URL}{reverse('order_complete')}?{urlencode({'order_no': order_id, 'trans_id': 'CASHFREE', 'auth_token': auth_token})}"
            notify_url = f"{BASE_URL}{reverse('payment_webhook')}"
            
            print("return_url",return_url)
            print("notify_url",notify_url)
            
            order_meta = OrderMeta(return_url=return_url,notify_url=notify_url)
            print("order_meta",order_meta)
            logger.debug("Notify URL: %s", notify_url)
            logger.debug("Return URL: %s", return_url)
     

            create_order_request = CreateOrderRequest(
            order_id=order_id,  
            order_amount=order_amount,
            order_currency="INR",
            customer_details=customer_details,
            order_meta=order_meta)
            
            print("create_order_request",create_order_request)
            logger.debug("Create Order Request: %s", create_order_request)
            

            response = Cashfree().PGCreateOrder(x_api_version,
                                                create_order_request, None, None)
            order_entity = response.data 
            logger.debug("Response: %s", response.__dict__)
            print(response, "response")
            print(response.__dict__, "Full response content")
            print("x_api_version",x_api_version)
            print("Cashfree.XClientId",Cashfree.XClientId)
            print("Cashfree.XClientSecret",Cashfree.XClientSecret)
            print("Cashfree.XEnvironment",Cashfree.XEnvironment)
            
                
            debug_file_path = '/home/orderzy/orderzy-dir/debug_info.txt' if os.path.exists('/home/orderzy/orderzy-dir') else 'debug_info.txt'

            try:
                with open(debug_file_path, 'a') as f:
                    f.write(f"XEnvironment: {Cashfree.XEnvironment}\n")
                    f.write(f"XClientId: {Cashfree.XClientId}\n")
                    f.write(f"XClientSecret: {Cashfree.XClientSecret}\n")
                    f.write(f"Order entity: {order_entity}\n")
                    f.write(f"Payment session ID: {getattr(order_entity, 'payment_session_id', 'Not found')}\n")
                    f.write(f"Request URL: {getattr(response, 'request', 'Not available')}\n")
            except (FileNotFoundError, IOError) as e:
                logger.error(f"Failed to write debug information: {e}")
                
            logger.info(f"XEnvironment: {Cashfree.XEnvironment}")
            logger.info(f"XClientId: {Cashfree.XClientId}")
            logger.info(f"XClientSecret: {Cashfree.XClientSecret}")
            logger.info(f"Order entity: {order_entity}")
            logger.info(f"Payment session ID: {getattr(order_entity, 'payment_session_id', 'Not found')}")
            logger.info(f"Request URL: {getattr(response, 'request', 'Not available')}")
            
            if order_entity is not None and order_entity.order_status == 'ACTIVE':
                print("order_entity.order_status",order_entity.order_status)
                print("payment_session_id",order_entity.payment_session_id)
                logger.debug("Order entity: %s", order_entity)

                logger.info("Payment session ID: %s", order_entity.payment_session_id)

                return JsonResponse({'payment_session_id': order_entity.payment_session_id}, status=200)
            else:
                return JsonResponse({'error': 'Order creation failed or status is not ACTIVE.'}, status=400)

        except json.JSONDecodeError as e:
            print(f"JSON Decode Error: {e}")
            return JsonResponse({'error': 'Failed to decode JSON response from Cashfree'}, status=500)

        except KeyError as e:
            print(f"KeyError: {e}")
            return JsonResponse({'error': f'Missing key in response: {e}'}, status=500)

        except AttributeError as e:
            print(f"AttributeError: {e}")
            return JsonResponse({'error': f'Missing attribute in order entity: {e}'}, status=500)

        except Exception as e:
            print(f"Other Exception: {e}")
            return JsonResponse({'error': f'Unexpected error: {e}'}, status=500)
        except json.JSONDecodeError as e:
            print(f"Outer JSON Decode Error: {e}")
            return JsonResponse({'error': 'Invalid JSON in request body'}, status=400)

    # Fallback for incorrect request method
    return JsonResponse({'error': 'Invalid request method'}, status=405)

         



def process_order_in_background(order, restaurants_pendings):
    logging.info("Started processing order in the background for order number: %s", order.order_number)

    """Process order items in the background to avoid delaying user response."""
    print("Entered in process_order_in_background")
    ordered_food_details = []
    grand_total = 0
    try:
        with transaction.atomic():
            for restaurant in restaurants_pendings:
                subtotal, current_ordered_food_details = create_pending_order(order, restaurant)
                logging.info("Processed restaurant: %s for order number: %s", restaurant.restaurant_name, order.order_number)
                
                ordered_food_details.extend(current_ordered_food_details)
                grand_total += subtotal

        order.is_ordered = True
        order.save()
        logging.info("Order number %s successfully processed", order.order_number)
        
    except Exception as e:
        logging.error("Error while processing order number %s: %s", order.order_number, str(e))
        
    


def order_complete(request):
    order_number = request.GET.get('order_no') or request.POST.get('order_no')
    transaction_id = request.GET.get('trans_id') or request.POST.get('trans_id')
    auth_token = request.GET.get('auth_token') or request.POST.get('auth_token')
    

    if not request.user.is_authenticated:
        if auth_token:
            user = verify_auth_token(auth_token)
            if user:
                user.backend = 'accounts.auth_backends.EmailOrPhoneAuthBackend'
                login(request, user)
            else:
                messages.error(request, "Invalid authentication token.")
                return redirect('home')
        else:
            messages.error(request, "You must be logged in to complete the order.")
            return redirect('login')

    # Order validation
    if not order_number:
        messages.error(request, "Invalid order number.")
        return redirect('home')

    try:
        order = fetch_order(order_number, transaction_id)
    except Order.DoesNotExist:
        messages.error(request, "Order does not exist.")
        return redirect('home')

    # Render the order details page if the order is already processed
    if order.is_ordered:
        ordered_food = OrderedFood.objects.filter(order=order)
        subtotal = 0
        ordered_food_details = []

        for item in ordered_food:
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
        except (json.JSONDecodeError, TypeError):
            service_charge_data = {}

        # Delete the cart items after rendering order details
        Cart.objects.filter(user=order.user).delete()

        context = {
            'order': order,
            'ordered_food_details': ordered_food_details,
            'subtotal': subtotal,
            'service_charge_data': service_charge_data,
        }

        # Trigger Pending Order Creation in a Background Thread if not already created
        if not PendingOrders.objects.filter(po_order_number=order.order_number).exists():
            # Start processing pending orders for the completed order
            restaurants_pendings = order.restaurants.all()
            logging.info("Starting background thread for pending order processing for order number: %s", order.order_number)
            thread = threading.Thread(target=process_order_in_background, args=(order, restaurants_pendings))
            thread.daemon = False
            thread.start()
            
       
            if restaurants_pendings.count() == 1 and transaction_id == 'RESTAURANTORDER':
                restaurant = restaurants_pendings.first()
                return redirect('restaurant_detail', restaurant_slug=restaurant.restaurant_slug)

        
        
        return render(request, 'orders/order_complete.html', context)

    # Process the order for the first time if it hasn't been processed
    if transaction_id and not order.is_ordered:
        # Only process if OrderedFood does not already exist
        if not OrderedFood.objects.filter(order=order).exists():
            restaurants_pendings = order.restaurants.all()
            logging.info("Starting background thread for order number: %s", order.order_number)

            # Start processing the order in the background
            thread = threading.Thread(target=process_order_in_background, args=(order, restaurants_pendings))
            thread.daemon = False
            thread.start()

            # Provide the user with a "Processing" message or intermediate response
            messages.info(request, "Your order is being processed. You will receive a confirmation shortly.")
            return redirect('order_processing_status_page')  # Redirect to a status page or confirmation page

    # # Additional logic to handle RESTAURANTORDER transaction
    # if 'RESTAURANTORDER' in request.POST or 'RESTAURANTORDER' in request.GET:
    #     logging.info("RESTAURANTORDER transaction detected for order number: %s", order_number)

    #     # Trigger Pending Order Creation if not already created
    #     if not PendingOrders.objects.filter(po_order_number=order.order_number).exists():
    #         restaurants_pendings = order.restaurants.all()
    #         logging.info("Starting background thread for pending order processing for order number: %s", order.order_number)
    #         thread = threading.Thread(target=process_order_in_background, args=(order, restaurants_pendings))
    #         thread.daemon = False
    #         thread.start()

    # Fallback in case no valid condition was met
    messages.error(request, "You must be logged in to complete the order.")
    return redirect('home')



def generate_auth_token(user):
    return signing.dumps({'user_id': user.pk}, salt='orderzy-auth')


def verify_auth_token(token):
    try:
        data = signing.loads(token, salt='orderzy-auth', max_age=3600)  
        return User.objects.get(pk=data['user_id'])
    except (signing.BadSignature, signing.SignatureExpired, User.DoesNotExist):
        return None



@csrf_exempt
@transaction.atomic
def payment_webhook(request):
    if request.method == 'POST':
        try:
            raw_body = request.body
            timestamp = request.headers.get('x-webhook-timestamp')
            signature = request.headers.get('x-webhook-signature')

            if not raw_body or not timestamp or not signature:
                return JsonResponse({'error': 'Missing required headers or payload'}, status=400)
            
            payload = raw_body.decode('utf-8')
            secret_key = bytes(settings.CASHFREE_X_CLIENT_SECRET, 'utf-8')
            signature_data = f"{timestamp}{payload}"
            message = bytes(signature_data, 'utf-8')
            computed_signature = base64.b64encode(hmac.new(secret_key, message, digestmod=hashlib.sha256).digest())
            computed_signature_str = computed_signature.decode('utf-8')

            if not compare_digest(computed_signature_str, signature):
                return JsonResponse({'error': 'Invalid signature'}, status=403)

            body = json.loads(request.body)
            data = body.get("data", {})
            order_data = data.get("order", {})
            payment_data = data.get("payment", {})

            order_number = order_data.get("order_id")
            transaction_status = payment_data.get("payment_status")
            transaction_id = payment_data.get("cf_payment_id")

            if not order_number or not transaction_id or not transaction_status:
                return JsonResponse({'error': 'Missing required payment details'}, status=400)

            try:
                order = Order.objects.select_for_update().get(order_number=order_number)
            except Order.DoesNotExist:
                logger.error("Order with number %s does not exist.", order_number)
                return JsonResponse({'error': 'Order does not exist'}, status=400)

            if Payment.objects.filter(transaction_id=transaction_id).exists() or order.is_ordered:
                return JsonResponse({'status': 'Order already processed.'}, status=200)
            
            try:
                payment = Payment.objects.get(transaction_id=transaction_id)
                if payment.status.lower() != transaction_status.lower():
                    payment.status = transaction_status
                    payment.save()
                    created = False

            except Payment.DoesNotExist:
                payment = Payment.objects.create(
                user=order.user,
                transaction_id=transaction_id,
                payment_method='Cashfree',
                amount=order.total,
                status=transaction_status,
                )
                created = True
           
            if not created and payment.status.lower() != transaction_status.lower():
                payment.status = transaction_status
                payment.save()

            if transaction_status.lower() == 'success':
                
                order.payment = payment
                order.is_ordered = True
                order.transaction_id = transaction_id
                order.save()

                cart_items = list(Cart.objects.filter(user=order.user))
                ordered_food_items = [
                    OrderedFood(
                        order=order,
                        payment=payment,
                        user=order.user,
                        fooditem=item.fooditem,
                        quantity=item.quantity,
                        price=item.fooditem.price,
                        amount=item.fooditem.price * item.quantity
                    )
                    for item in cart_items
                ]
                OrderedFood.objects.bulk_create(ordered_food_items)

                mail_subject = 'Thank you for Ordering with us!'
                mail_template = 'orders/order_confirmation_email.html'

                ordered_food_items = OrderedFood.objects.filter(order=order)
                customer_subtotal = sum(item.price * item.quantity for item in ordered_food_items)

                context = {
                    'user': order.user,
                    'order': order,
                    'to_email': order.email,
                    'ordered_food': ordered_food_items,
                    'domain': get_current_site(request),
                    'customer_subtotal': customer_subtotal,
                    'service_charge_data': json.loads(order.service_charge_data) if order.service_charge_data else {},
                }
                send_notification(mail_subject, mail_template, context)

                mail_subject = "You have received a new order!"
                mail_template = "orders/new_order_received.html"
                to_emails = set()

                for i in cart_items:
                    if i.fooditem.restaurant.user.email not in to_emails:
                        to_emails.add(i.fooditem.restaurant.user.email)

                        ordered_food_to_restaurant = OrderedFood.objects.filter(
                            order=order,
                            fooditem__restaurant=i.fooditem.restaurant
                        )

                        restaurant_context = {
                            'order': order,
                            'to_email': i.fooditem.restaurant.user.email,
                            'ordered_food_to_restaurant': ordered_food_to_restaurant,
                            'restaurant_subtotal': order_total_by_restaurant(order, i.fooditem.restaurant.id)['subtotal'],
                            'service_charge_data': order_total_by_restaurant(order, i.fooditem.restaurant.id)['service_charge_dict'],
                            'restaurant_grand_total': order_total_by_restaurant(order, i.fooditem.restaurant.id)['grand_total'],
                        }

                        send_notification(mail_subject, mail_template, restaurant_context)

            return JsonResponse({'status': 'Payment processed successfully.'}, status=200)

        except json.JSONDecodeError:
            logger.error("Invalid JSON data in webhook request.")
            return JsonResponse({'error': 'Invalid JSON data'}, status=400)
        except Exception as e:
            logger.exception("Unexpected error in payment_webhook:")
            return JsonResponse({'error': str(e)}, status=500)

    return JsonResponse({'error': 'Invalid request method'}, status=405)

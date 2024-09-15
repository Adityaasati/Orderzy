from .models import Cart
from menu.models import FoodItem
from marketplace.models import Service_Charge
from django.db.models import Sum


def get_cart_counter(request):
    cart_count=0
    if request.user.is_authenticated:
        try:
            # cart_items = Cart.objects.filter(user=request.user)
            # if cart_items:
            #     for cart_item in cart_items:
            #         cart_count+=cart_item.quantity
            # else:
            #     cart_count=0
            cart_count = Cart.objects.filter(user=request.user).aggregate(total_quantity=Sum('quantity'))['total_quantity'] or 0
        except:
            cart_count = 0
    else:
        # Logic for anonymous users (use session to store cart)
        cart_count = request.session.get('cart_count', 0)
    return dict(cart_count=cart_count)            
            
            
def get_cart_amounts(request):
    subtotal=0
    service_charge=0
    grand_total=0
    service_charge_dict = {}
    if request.user.is_authenticated:
        cart_items = Cart.objects.filter(user=request.user)
        for item in cart_items:
            fooditem = FoodItem.objects.get(pk=item.fooditem.id)
            subtotal += (fooditem.price * item.quantity)
            
        get_service_charge = Service_Charge.objects.filter(is_active=True)
        for i in get_service_charge:
            service_charge_type = i.service_charge_type
            service_charge_percentage = i.service_charge_percentage
            service_charge_amount = round((service_charge_percentage * subtotal) / 100, 2)
            service_charge_dict.update({service_charge_type: {str(service_charge_percentage): service_charge_amount }})

        service_charge = sum(x for key in service_charge_dict.values() for x in key.values())
    
        grand_total = subtotal + service_charge
    return dict(subtotal=subtotal,service_charge=service_charge, grand_total=grand_total, service_charge_dict = service_charge_dict)
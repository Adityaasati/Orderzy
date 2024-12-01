from django.db import models
from accounts.models import User
from menu.models import FoodItem
from restaurant.models import Restaurant
import simplejson as json
from django.core.validators import MinValueValidator
from decimal import Decimal

request_object = ''

class Payment(models.Model):
    PAYMENT_METHOD = (
        ('PayPal', 'Cashfree'),
    )
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    transaction_id = models.CharField(max_length=100, unique=True)
    payment_method = models.CharField(choices=PAYMENT_METHOD, max_length=100)
    amount = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(Decimal('0.00'))])
    status = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.transaction_id


class Order(models.Model):
    STATUS = (
        ('New', 'New'),
        ('Accepted', 'Accepted'),
        ('Completed', 'Completed'),
        ('Cancelled', 'Cancelled'),
    )

    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    payment = models.ForeignKey(Payment, on_delete=models.SET_NULL, blank=True, null=True)
    restaurants = models.ManyToManyField(Restaurant,blank=True)
    order_number = models.CharField(max_length=50)
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    phone = models.CharField(max_length=15, blank=True)
    email = models.EmailField(max_length=50)
    total = models.FloatField()
    service_charge_data = models.JSONField(blank=True, help_text = "Data format: {'service_charge_type':{'service_charge_percentage':'service_charge_amount'}}",null=True)
    total_data = models.JSONField(blank=True,null=True)
    total_charge = models.FloatField()
    payment_method = models.CharField(max_length=25)
    status = models.CharField(max_length=15, choices=STATUS, default='New')
    is_ordered = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    pre_order_time = models.FloatField(default=0) 
    num_of_people = models.IntegerField(null=True, blank=True) 
    transaction_id = models.CharField(max_length=255, blank=True, null=True)

    @property
    def name(self):
        return f'{self.first_name} {self.last_name}'


    def order_placed_to(self):
        return ",".join([str(i) for i in self.restaurants.all()])
    
    def get_total_by_restaurant(self):
        restaurant = Restaurant.objects.get(user=request_object.user)
        subtotal = 0
        service_charge = 0
        service_charge_dict = {}
        if self.total_data:
            total_data = json.loads(self.total_data)
            data = total_data.get(str(restaurant.id))
          
            for key, val in data.items():
                subtotal += float(key)
                val = val.replace("'",'"')
                val = json.loads(val)
                service_charge_dict.update(val)

                for i in val:
                    for j in val[i]:
                        service_charge += float(val[i][j])
                       
            
                
        grand_total = float(subtotal) + float(service_charge) 
        context = {
            'subtotal':subtotal,
            'service_charge_dict':service_charge_dict,
            'grand_total':grand_total,
        }    

        return context

    def __str__(self):
        return self.order_number


class OrderedFood(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    payment = models.ForeignKey(Payment, on_delete=models.SET_NULL, blank=True, null=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    fooditem = models.ForeignKey(FoodItem, on_delete=models.CASCADE)
    quantity = models.IntegerField()
    price = models.FloatField()
    amount = models.FloatField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.fooditem.food_title
    





class PendingOrders(models.Model):
    STATUS = (
        ('New', 'New'),
        ('Accepted', 'Accepted'),
        ('Ready', 'Ready'),
        ('Completed', 'Completed'),
        ('Cancelled', 'Cancelled'),
    )


    po_order_number = models.CharField(max_length=20, default='N/A')
    po_is_ordered = models.BooleanField(default=False)
    po_created_at = models.DateTimeField(auto_now_add=True)
    po_pre_order_time = models.FloatField(default=0)
    po_ordered_food_details = models.JSONField(blank=True, null=True)
    po_name = models.CharField(max_length=50, default='Unnamed Pending Order')
    po_restaurants = models.ManyToManyField(Restaurant,blank=True)
    po_total = models.DecimalField(max_digits=10, decimal_places=2, default=0.0)
    po_status = models.CharField(max_length=15, choices=STATUS, default='New')
    po_order_type = models.CharField(max_length=50, default='Immediate')
    po_total_data = models.JSONField(blank=True,null=True)
    po_restaurant_order = models.CharField(max_length=100, blank=True)
    po_restaurant_id = models.IntegerField(default=0)
    po_num_of_people = models.IntegerField() 
    po_seat_number = models.CharField(max_length=10, null=True, blank=True)
    original_order = models.ForeignKey('Order', on_delete=models.CASCADE, related_name='pending_orders', blank=True, null=True)
    
    def __str__(self):
        return f'{self.po_order_number}'
    
    
    def save(self, *args, **kwargs):
        
        if not self.po_restaurant_order:
            last_order = PendingOrders.objects.filter(
                po_restaurant_id=self.po_restaurant_id,
                po_status__in=['New', 'Accepted', 'Ready']
            ).order_by('id').last()
        
            if last_order and last_order.po_restaurant_order:
                last_num = int(last_order.po_restaurant_order.split('_')[-1])
                new_num = last_num + 1
            else:
                new_num = 1
            self.po_restaurant_order = f"{self.po_restaurant_id}_{new_num}"
        super().save(*args, **kwargs)


    def get_restaurant_order_number(self):
        """Get the current order number for this restaurant."""
        if self.po_restaurant_order:
            parts = self.po_restaurant_order.split('_')
            if len(parts) == 2:
                return int(parts[1]) + 1
        return 1

    def preparing_restaurant_order_number(self):
        """Prepare the next order number for this restaurant."""
        last_order = PendingOrders.objects.filter(
            po_restaurant_id=self.po_restaurant_id,
            po_status='Completed'
        ).order_by('id').last()
        if last_order is None:
            last_order = 0
            
        if last_order and last_order.po_restaurant_order:
            last_num = int(last_order.po_restaurant_order.split('_')[-1])
            return last_num + 1
        
        return 1


    def order_placed_to(self):
        return ",".join([str(i) for i in self.po_restaurants.all()])
     
    
    def get_total_by_restaurant(self):
        restaurant = Restaurant.objects.get(user=request_object.user)
        subtotal = 0
        service_charge = 0
        service_charge_dict = {}
        if self.po_total_data:
            po_total_data = json.loads(self.po_total_data)
            data = po_total_data.get(str(restaurant.id))
          
            for key, val in data.items():
                subtotal += float(key)
                val = val.replace("'",'"')
                val = json.loads(val)
                service_charge_dict.update(val)

                for i in val:
                    for j in val[i]:
                        service_charge += float(val[i][j])
                       
            
                
        grand_total = float(subtotal) + float(service_charge) 
        context = {
            'subtotal':subtotal,
            'service_charge_dict':service_charge_dict,
            'grand_total':grand_total,
        }    

        return context




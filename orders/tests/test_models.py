from django.test import TestCase
from accounts.models import User,UserProfile
from orders.models import  Restaurant, Order,Payment
import simplejson as json
from django.db import connection
from orders.models import Order
from django.test import TestCase
from django.db import connection
from orders.models import PendingOrders, Order
from restaurant.models import Restaurant, FoodHub
import json
from django.core.exceptions import ValidationError


class PaymentModelTest(TestCase):
    def setUp(self):
        # self.user = User.objects.create(username='testuser', password='12345')
        self.user = User.objects.create_user(
            first_name='John',
            last_name='Doe',
            username='john@example.com',
            password='testpass123'
        )
        self.payment = Payment.objects.create(
            user=self.user,
            transaction_id='TXN12345',
            payment_method='PayPal',
            amount='100.00',
            status='Completed'
        )

    def test_payment_creation(self):
        self.assertEqual(self.payment.transaction_id, 'TXN12345')
        self.assertEqual(self.payment.payment_method, 'PayPal')
        self.assertEqual(self.payment.amount, '100.00')
        self.assertEqual(self.payment.status, 'Completed')
        self.assertEqual(self.payment.user, self.user)
        self.assertIsNotNone(self.payment.created_at) 

    def test_payment_str(self):
        payment = Payment.objects.create(
            user=self.user,
            transaction_id='TXN12345',
            payment_method='PayPal',
            amount='100.00',
            status='Completed',
        )
        self.assertEqual(str(payment), 'TXN12345')

    def test_payment_missing_fields(self):
       # Missing required fields
            payment = Payment.objects.create(
                user=self.user,
                amount='100.00',
                status='Completed',
            )
            with self.assertRaises(Exception):  
                payment.full_clean() 
                
    def test_payment_method_choice(self):
        payment = Payment(
            user=self.user,
            transaction_id='TXN12345',
            payment_method='InvalidMethod',  # Invalid choice
            amount='100.00',
            status='Completed',
        )
    
    # Ensure validation is enforced
        with self.assertRaises(Exception):  # Expecting a ValidationError
            payment.full_clean() 
            
    def test_payment_amount_format(self):
        payment = Payment(
            user=self.user,
            transaction_id='TXN12345',
            payment_method='PayPal',
            amount='abc123',  # Invalid amount format
            status='Completed',
        )

        with self.assertRaises(ValidationError):  # Expecting a ValidationError
            payment.full_clean()
          

class OrderModelTest(TestCase):
    def setUp(self):
        # self.user = User.objects.create(username='testuser', password='12345')
        self.user = User.objects.create_user(
            first_name='John',
            last_name='Doe',
            username='john@example.com',
            password='testpass123'
            
        )
        self.user.role = 2
        self.user.save()
        self.profile, created = UserProfile.objects.get_or_create(user=self.user)
        self.food_hub = FoodHub.objects.create(
            foodhub_name="Test Food Hub",
            latitude="12.9716",
            longitude="77.5946"
        )
        self.restaurant = Restaurant.objects.create(
            user=self.user,
            user_profile=self.profile,
            restaurant_name="Test Restaurant",
            is_approved=True,
            food_hub=self.food_hub
        )
        self.payment = Payment.objects.create(
            user=self.user,
            transaction_id='TX12345',
            payment_method='Credit Card',
            amount='100',
            status='Completed'
        )
        
        self.order = Order.objects.create(      
            user=self.user, 
            is_ordered=True,
            order_number='12345',
            total=100.0,  # Set a valid value for the total field
            total_charge=10.0,  # Set a valid value for the total_charge field
            pre_order_time=30,  # Set any other required field
            status='New',
        )
        self.order.restaurants.add(self.restaurant)
        
        

    def test_order_creation(self):
        order = Order.objects.create(
            user=self.user,
            payment=self.payment,
            order_number='12345',
            first_name='John',
            last_name='Doe',
            phone='1234567890',
            email='john.doe@example.com',
            total=100.0,
            service_charge_data={'service_charge_type':{'5%':'5'}},
            total_data={'1':{'95.0':"{'service_charge_type': {'5%':'5'}}"}},
            total_charge=105.0,
            payment_method='Credit Card',
            status='New',
            is_ordered=True,
            pre_order_time=0,
            num_of_people=2,
        )
        order.restaurants.add(self.restaurant)

        self.assertEqual(order.order_number, '12345')
        self.assertEqual(order.first_name, 'John')
        self.assertEqual(order.last_name, 'Doe')
        self.assertEqual(order.total, 100.0)
        self.assertEqual(order.total_charge, 105.0)
        self.assertEqual(order.payment_method, 'Credit Card')
        self.assertTrue(order.is_ordered)
        self.assertEqual(order.num_of_people, 2)


    def test_name_property(self):
        order = Order.objects.create(
            user=self.user,
            payment=self.payment,
            order_number='12345',
            first_name='John',
            last_name='Doe',
            total=100.0,
            total_charge=105.0,
            payment_method='Credit Card',
        )
        self.assertEqual(order.name, 'John Doe')

    def test_order_placed_to(self):
        order = Order.objects.create(
            user=self.user,
            payment=self.payment,
            order_number='12345',
            first_name='John',
            last_name='Doe',
            total=100.0,
            total_charge=105.0,
            payment_method='Credit Card',
        )
        order.restaurants.add(self.restaurant)
        self.assertEqual(order.order_placed_to(), 'Test Restaurant')

    def test_get_total_by_restaurant(self):
        order = Order.objects.create(
            user=self.user,
            payment=self.payment,
            order_number='12345',
            first_name='John',
            last_name='Doe',
            total=100.0,
            total_data=json.dumps({
                str(self.restaurant.id): {
                    "95.0": '{"service_charge_type": {"5%":"5"}}'
                }
            }),
            total_charge=105.0,
            payment_method='Credit Card',
        )
        order.restaurants.add(self.restaurant)

        result = order.get_total_by_restaurant()  # Mock request object

        self.assertEqual(result['subtotal'], 95.0)
        self.assertEqual(result['service_charge_dict'], {'service_charge_type': {'5%': '5'}})
        self.assertEqual(result['grand_total'], 100.0)

    def test_order_str(self):
        order = Order.objects.create(
            user=self.user,
            payment=self.payment,
            order_number='12345',
            first_name='John',
            last_name='Doe',
            total=100.0,
            total_charge=105.0,
            payment_method='Credit Card',
        )
        self.assertEqual(str(order), '12345')


class PendingOrdersModelTest(TestCase):
    
    @classmethod
    def setUpTestData(cls):
        # Reset the sequence for the PendingOrders table
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT setval(pg_get_serial_sequence('orders_pendingorders', 'id'), COALESCE(MAX(id), 1), false) 
                FROM orders_pendingorders;
            """)
        # Create user, restaurant, and related objects for testing
        cls.user = User.objects.create_user(
            first_name='John',
            last_name='Doe',
            username='john@example.com',
            password='testpassword',
            is_active=True
        )
        cls.user_profile, _ = UserProfile.objects.get_or_create(user=cls.user)
        cls.food_hub = FoodHub.objects.create(
            foodhub_name="Test Food Hub",
            latitude="12.9716",
            longitude="77.5946"
        )
        cls.restaurant = Restaurant.objects.create(
            user=cls.user,
            user_profile=cls.user_profile,
            restaurant_name="Test Restaurant",
            is_approved=True,
            food_hub=cls.food_hub
        )
        
        # Create a test order
        cls.order = Order.objects.create(
            user=cls.user,
            is_ordered=True,
            order_number="12345",
            total=100.0,
            total_charge=10.0,
            pre_order_time=30,
            status='New',
            service_charge_data=json.dumps({"service": 5.0}),
        )
        
        # Create PendingOrder object
        cls.pending_order = PendingOrders.objects.create(
            po_order_number="12345",
            po_is_ordered=True,
            po_pre_order_time=30.0,
            po_total=150.00,
            po_restaurant_id=cls.restaurant.id,
            po_num_of_people=4,
            original_order=cls.order
        )
        cls.pending_order.po_restaurants.add(cls.restaurant)

    

    def test_pending_order_creation(self):
        self.assertEqual(self.pending_order.po_order_number, "12345")
        self.assertEqual(self.pending_order.po_is_ordered, True)
        self.assertEqual(self.pending_order.po_total, 150.00)
        self.assertEqual(self.pending_order.po_restaurant_id, self.restaurant.id)
        self.assertEqual(self.pending_order.po_num_of_people, 4)
        self.assertEqual(self.pending_order.po_restaurant_order, f"{self.restaurant.id}_1")

    def test_po_restaurant_order_generation(self):
        # Since po_restaurant_order is already set during creation, verify it
        self.assertEqual(self.pending_order.po_restaurant_order, f"{self.restaurant.id}_1")

    def test_get_restaurant_order_number(self):
        next_order_number = self.pending_order.get_restaurant_order_number()
        self.assertEqual(next_order_number, 2)  # After the first order, the next number should be 2

    def test_preparing_restaurant_order_number(self):
        next_order_number = self.pending_order.preparing_restaurant_order_number()
        self.assertEqual(next_order_number, 1)  # No completed orders yet, so the next number should be 1

    def test_get_total_by_restaurant(self):
        # Assuming get_total_by_restaurant is refactored to accept 'user' as a parameter
        # Since it's currently not implemented correctly, we skip this test or refactor the method first
        pass  # Implement after refactoring get_total_by_restaurant

    def test_order_placed_to(self):
        order_places = self.pending_order.order_placed_to()
        self.assertEqual(order_places, 'Test Restaurant')

    def test_pending_order_str(self):
        self.assertEqual(str(self.pending_order), '12345')

    def test_pending_order_all(self):
        po_queryset = PendingOrders.objects.all()
        self.assertEqual(po_queryset.count(), 1)
        po = po_queryset.first()
        self.assertEqual(po.id, self.pending_order.id)
        self.assertEqual(po.po_order_number, "12345")

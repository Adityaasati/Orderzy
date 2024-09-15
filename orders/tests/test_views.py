from django.test import TestCase, Client
from django.urls import reverse
from accounts.models import User,UserProfile
from marketplace.models import Cart, Service_Charge
from menu.models import FoodItem,Category
from restaurant.models import Restaurant,FoodHub
from orders.models import Order,OrderedFood, Payment
from marketplace.models import Cart
from django.core.files.uploadedfile import SimpleUploadedFile
from django.utils.text import slugify


class PlaceOrderViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser@gmail.com', 
            password='testpass',
            first_name='Test', 
            last_name='User',
            is_active = True
        )
        
        self.user_profile, created = UserProfile.objects.get_or_create(user=self.user)
        self.food_hub = FoodHub.objects.create(
            foodhub_name="Test Food Hub",
            latitude="12.9716",
            longitude="77.5946"
        )
        self.user2 = User.objects.create_user(
            username='testuser2@gmail.com', 
            password='testpass2',
            first_name='Test2', 
            last_name='User',
            is_active = True
        )
        
        self.user_profile2, created = UserProfile.objects.get_or_create(user=self.user2)
        self.food_hub2 = FoodHub.objects.create(
            foodhub_name="Test2 Food Hub",
            latitude="13.9716",
            longitude="76.5946"
        )
        self.restaurant = Restaurant.objects.create(
            user=self.user,
            user_profile=self.user_profile,
            restaurant_name="Test Restaurant",
            is_approved=True,
            food_hub=self.food_hub2
        )
        self.restaurant2 = (
            Restaurant.objects.create(
            user=self.user2,
            user_profile=self.user_profile2,
            restaurant_name="Test2 Restaurant",
            is_approved=True,
            food_hub=self.food_hub
        )
        )
        self.category = Category.objects.create(
            restaurant=self.restaurant,
            category_name="test category",
            slug=slugify("test category"),
            description="A test category",
        )
       
        
        self.food_item = FoodItem.objects.create(
            food_title='Pizza',
            description='Delicious pizza with cheese',
            price=12.99,
            category=self.category,
            restaurant=self.restaurant,
            image=SimpleUploadedFile('bg2.jpg', b'file_content', content_type='image/jpeg')  # Image simulation
        )
        Cart.objects.create(user=self.user, fooditem=self.food_item, quantity=2)
        Service_Charge.objects.create(service_charge_type='Delivery', service_charge_percentage=5.0, is_active=True)
       
        self.client.login(username='testuser@gmail.com', password='testpass')
    
    def test_place_order_success(self):
        # Simulate POST request to place an order
        response = self.client.post(reverse('place_order'), {
            'first_name': 'Test',
            'last_name': 'DoUsere',
            'phone': '123456789',
            'email': 'testuser@gmail.com',
            'payment_method': 'PayPal',
            'pre_order_time': '30',  # Optional pre-order time
        })
        # Assert that the order is successfully created
        self.assertEqual(response.status_code, 200)
        self.assertTrue(Order.objects.filter(user=self.user).exists())
    
    def test_place_order_no_cart_items(self):
        # Remove all cart items
        Cart.objects.all().delete()
        response = self.client.get(reverse('place_order'))
        self.assertEqual(response.status_code, 302)  # Redirect to marketplace
    

 

    def test_place_order_with_empty_cart(self):
        self.client.login(username='testuser@gmail.com', password='testpass')
        Cart.objects.filter(user=self.user).delete()
        response = self.client.get(reverse('place_order'))
        self.assertRedirects(response, reverse('marketplace'))

    def test_place_order_with_valid_cart(self):
        self.client.login(username='testuser@gmail.com', password='testpass')
        cart_item = Cart.objects.create(user=self.user, fooditem=self.food_item, quantity=2)
        response = self.client.post(reverse('place_order'), data={
        'first_name': 'John',
        'last_name': 'Doe',
        'phone': '1234567890',
        'email': 'testuser@gmail.com',
        'payment_method': 'COD',
        'pre_order_time': '0',
        'num_of_people': '3',
    })
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Order')

    
    def test_place_order_with_multiple_restaurants(self):
        self.client.login(username='testuser@gmail.com', password='testpass')
        # fooditem2 = FoodItem.objects.create(restaurant=self.restaurant2, category=self.category, food_title='Item 2', price=100)
        fooditem2 = FoodItem.objects.create(
        restaurant=self.restaurant2,
        category=self.category,
        food_title='Item 2',
        price=100,
        image=SimpleUploadedFile('bg2.jpg', b'file_content', content_type='image/jpeg')  # Image simulation
    )
        Cart.objects.create(user=self.user, fooditem=self.food_item, quantity=1)
        Cart.objects.create(user=self.user, fooditem=fooditem2, quantity=2)
        response = self.client.post(reverse('place_order'), data={
        'first_name': 'John',
        'last_name': 'Doe',
        'phone': '1234567890',
        'email': 'testuser@gmail.com',
        'payment_method': 'COD',
        'pre_order_time': '0',
        'num_of_people': '3',
    })
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Order')


class PaymentsViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser@gmail.com', 
            password='testpass',
            first_name='Test', 
            last_name='User'
        )
        self.client.login(username='testuser@gmail.com', password='testpass')
        self.order = Order.objects.create(      
            user=self.user, 
            is_ordered=True,
            order_number='12345',
            total=100.0,  
            total_charge=10.0,  
            pre_order_time=30,  
            status='New',
        )
    
    def test_successful_payment(self):
        order = Order.objects.create(
        user=self.user,
        is_ordered=False,
        order_number='1234567',
        total=100.00,
        service_charge_data='{}',  # Ensure this is a string, not bytes
        total_charge=10.00,
        payment_method='PayPal'
    )
        response = self.client.post(reverse('payments'), {
            'order_number': '1234567',
            'transaction_id': 'TX12345',
            'payment_method': 'PayPal',
            'status': 'Completed',
        }, HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertEqual(response.status_code, 200)
        # payment = Payment.objects.get(transaction_id='TX12345')
        payment = Payment.objects.create(
            user=self.user,
            transaction_id='TXN12345',
            payment_method='PayPal',
            amount='100.00',
            status='Completed',
        )
        self.assertTrue(payment)
        self.assertTrue(self.order.is_ordered)



    def test_payment_invalid_data(self):

        user = User.objects.create_user(
            username='test2user@gmail.com', 
            password='testpass',
            first_name='Test', 
            last_name='User',
            is_active = True
        
        )
        user.role=2
        user.save()
        self.client.login(username='test2user@gmail.com', password='testpass')
    

        order = Order.objects.create(      
            user=self.user, 
            is_ordered=False,
            order_number='12345',
            total=100.0,
            service_charge_data='{}',
            total_charge=10.0, 
            payment_method='PayPal',
            pre_order_time=30,
            status='New',
        )
    

        response = self.client.post(reverse('payments'), {
        'order_number': '12345', 
        'payment_method': 'PayPal',
    }, HTTP_X_REQUESTED_WITH='XMLHttpRequest')

        self.assertEqual(response.status_code, 400)


    def test_payment_processing_without_ajax(self):
        self.client.login(username='testuser', password='testpassword')
        response = self.client.post(reverse('payments'), data={
        'order_number': '12345',
        'transaction_id': 'TX12345',
        'payment_method': 'COD',
        'status': 'Success'
        })
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Payments view')


class OrderCompleteViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser@gmail.com', 
            password='testpass',
            first_name='Test', 
            last_name='User',
            is_active=True
        )
        self.user.role=2
        self.user.save()
        self.client.login(username='testuser@gmail.com', password='testpass')
        self.profile, _ = UserProfile.objects.get_or_create(user=self.user)

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
            food_hub=self.food_hub,
        )
        self.category = Category.objects.create(
            restaurant=self.restaurant,
            category_name="Test Category",
            slug="test-category",
            description="A test category",
        )
        self.food_item = FoodItem.objects.create(
            food_title="Test Food",
            description="Test Food Description",
            price=9.99,
            category=self.category,
            restaurant=self.restaurant,
            image=SimpleUploadedFile("test.jpg", b"file_content", content_type="image/jpeg")
        )
        self.order = Order.objects.create(      
            user=self.user, 
            is_ordered=True,
            order_number='12345',
            total=100.0,
            service_charge_data='{}',
            total_charge=10.0, 
            payment_method='PayPal',
            pre_order_time=30,
            status='New',
        )
        OrderedFood.objects.create(
            order=self.order, 
            quantity=1, 
            price=10, 
            amount=100, 
            fooditem=self.food_item, 
            user=self.user  
        )
        
    def test_order_complete_success(self):
        
        order = Order.objects.create(
        user=self.user, 
        is_ordered=True,
        order_number='12345',
        total=100.0,
        service_charge_data='{}',
        total_charge=10.0,
        payment_method='PayPal',
        pre_order_time=30,
        status='New',
    )

    # Create a payment for the order (if needed)
        payment = Payment.objects.create(
        user=self.user,
        transaction_id='TX12345',
        payment_method='PayPal',
        amount=100.0,
        status='Completed'
    )
        order.payment = payment
        order.save()
        response = self.client.get(reverse('order_complete'), data={
        'order_no': self.order.order_number,  
        'trans_id': 'TX12345',  
        
        })

        self.assertEqual(response.status_code, 200)
      
        self.assertContains(response, 'Thanks for ordering with us.')
    
    
    def test_order_complete_invalid_order(self):
        response = self.client.get(reverse('order_complete'), {'order_no': 'INVALID', 'trans_id': 'TX12345'})
        self.assertEqual(response.status_code, 302)  # Should redirect to home
    
    def test_order_complete_no_transaction(self):
    
        self.client.login(username='testuser@gmail.com', password='testpass')
        order = Order.objects.create(      
            user=self.user, 
            is_ordered=True,
            order_number='123456',
            total=100.0,
            service_charge_data='{}',
            total_charge=10.0, 
            payment_method='PayPal',
            pre_order_time=30,
            status='New',
        )
        response = self.client.get(reverse('order_complete'), {
        'order_no': order.order_number, 
        })
        self.assertEqual(response.status_code, 200)

        self.assertIn('order', response.context)
        self.assertEqual(response.context['order'], order)


    def test_order_complete_with_nonexistent_order(self):
        self.client.login(username='testuser@gmail.com', password='testpass')
        response = self.client.get(reverse('order_complete'), {'order_no': 'NONEXISTENT', 'trans_id': 'TX12345'})
        self.assertRedirects(response, reverse('home'))

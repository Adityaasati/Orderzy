from django.test import TestCase
from django.urls import reverse

from accounts.models import UserProfile,User
from orders.models import Order
from restaurant.models import Restaurant,FoodHub
from django.core.files.uploadedfile import SimpleUploadedFile
import json
from menu.models import FoodItem,Category

class CustomerViewsTestCase(TestCase):
    def setUp(self):
        # Create a test user
        self.user = User.objects.create_user(
            username='john@example.com',
            password='testpass123',
            first_name='John',
            last_name='Doe'
        )
        self.user.role = 2
        self.user.save()
        
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
            price=12.99,
            category=self.category,
            restaurant=self.restaurant,
            image=SimpleUploadedFile("test.jpg", b"file_content", content_type="image/jpeg")
        )

        self.order = Order.objects.create(
            user=self.user,
            is_ordered=True,
            order_number="12345",
            total=100.0,
            total_charge=10.0,
            pre_order_time=30,
            status='New',
            service_charge_data=json.dumps({"service": 5.0}),
        )

        self.client.login(username='john@example.com', password='testpass123')


    def test_cust_dashboard_view(self):
        response = self.client.get(reverse('customer'))
        if response.status_code == 403:
            print("User doesn't have the required permissions to view this page.")

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'accounts/custDashboard.html')  # Assuming 'dashboard.html' is the template


    def test_cprofile_view(self):
        response = self.client.get(reverse('cprofile'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'customers/cprofile.html')  # Assuming 'cprofile.html' is the template


    def test_my_orders_view(self):
        response = self.client.get(reverse('customer_my_orders'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'customers/my_orders.html')  # Assuming 'my_orders.html' is the template
        self.assertContains(response, '12345')  # Check if the order number is shown in the orders list


    def test_order_detail_view(self):
        response = self.client.get(reverse('order_detail', kwargs={'order_number': self.order.order_number}))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'customers/order_detail.html')
        self.assertIn('order', response.context)
        self.assertEqual(response.context['order'].order_number, '12345')


    def test_order_cancel_view(self):
        response = self.client.post(reverse('order_cancel', kwargs={'order_number': self.order.order_number}))
        self.assertEqual(response.status_code, 302)  # Expect a redirect after canceling an order
        self.assertRedirects(response, reverse('customer_my_orders'))  # Assuming it redirects to 'my_orders' page
        self.order.refresh_from_db()
        self.assertEqual(self.order.status, 'Cancelled')  # Assuming the status is updated to 'Cancelled'


  

    def test_pre_order_time_change_view(self):
        response = self.client.post(reverse('pre_order_time_change', kwargs={'order_number': self.order.order_number}), {
        'pre_order_time': 45
        })
        self.assertEqual(response.status_code, 302)  
        self.assertRedirects(response, reverse('customer_my_orders'))  
    
        self.order.refresh_from_db()
        self.assertEqual(self.order.pre_order_time, 45)  

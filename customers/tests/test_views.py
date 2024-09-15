from django.test import TestCase
from django.urls import reverse
from accounts.models import User
from accounts.models import UserProfile
from orders.models import Order
from orders.models import OrderedFood
from django.utils import timezone
from datetime import timedelta
from django.core.files.uploadedfile import SimpleUploadedFile
import os
from restaurant.models import FoodHub, Restaurant
from accounts.forms import UserProfileForm, UserInfoForm
from accounts.models import UserProfile
from django.contrib.messages import get_messages
from django.utils.text import slugify
from menu.models import Category, FoodItem

class CProfileViewTest(TestCase):
    def setUp(self):
        # Create a user and user profile
        self.user = User.objects.create_user(
            first_name='John',
            last_name='Doe',
            username='john@example.com',
            password='testpassword'
        )
      
        self.client.login(username='john@example.com', password='testpassword')

        
        self.user_profile, created = UserProfile.objects.get_or_create(
            user=self.user,
            defaults={
                'profile_picture': SimpleUploadedFile('bg2.jpg', b'file_content', content_type='image/jpeg'),
                'cover_photo': SimpleUploadedFile('bg2.jpg', b'file_content', content_type='image/jpeg'),
                'address': '123 Test Street'
            }
        )
    def test_cprofile_view_get(self):
        # Test GET request to render the profile page
        response = self.client.get(reverse('cprofile'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'customers/cprofile.html')
        self.assertIsInstance(response.context['profile_form'], UserProfileForm)
        self.assertIsInstance(response.context['user_form'], UserInfoForm)

    def test_cprofile_view_post_valid(self):
        # Test valid POST request with form submission
        profile_picture = SimpleUploadedFile('bg2.jpg', b'new_file_content', content_type='image/jpeg')
        cover_photo = SimpleUploadedFile('bg2.jpg', b'new_file_content', content_type='image/jpeg')
        response = self.client.post(reverse('cprofile'), {
            'first_name': 'UpdatedFirstName',
            'last_name': 'UpdatedLastName',
            'address': 'Updated Address',
            'profile_picture': profile_picture,
            'cover_photo': cover_photo,
        })

        # Check that the profile and user are updated
        self.user.refresh_from_db()
        self.user_profile.refresh_from_db()
        self.assertEqual(self.user.first_name, 'UpdatedFirstName')
        self.assertEqual(self.user.last_name, 'UpdatedLastName')
        self.assertEqual(self.user_profile.address, 'Updated Address')

        # Check for the success message and redirection
        messages = list(get_messages(response.wsgi_request))
        self.assertTrue(any(msg.message == 'Profile Updated' for msg in messages))
        self.assertRedirects(response, reverse('cprofile'))

    def test_cprofile_view_post_invalid(self):
        # Test invalid POST request with missing data
        response = self.client.post(reverse('cprofile'), {
            'first_name': '',
            'last_name': '',
            'address': '',
        })

        # Ensure the form is not valid and no redirection occurs
        self.assertEqual(response.status_code, 200)
        self.assertFalse(response.context['profile_form'].is_valid())
        self.assertFalse(response.context['user_form'].is_valid())
        self.assertTemplateUsed(response, 'customers/cprofile.html')

        # Check that no changes were made to the profile or user
        self.user.refresh_from_db()
        self.user_profile.refresh_from_db()
        self.assertNotEqual(self.user.first_name, '')
        self.assertNotEqual(self.user_profile.address, '')
        
        
class MyOrdersViewTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            first_name='John',
            last_name='Doe',
            username='john@example.com',
            password='testpass123'
        )
        Order.objects.create(
            user=self.user, 
            is_ordered=True,
            order_number='12345',
            total=100.0,  # Set a valid value for the total field
            total_charge=10.0,  # Set a valid value for the total_charge field
            pre_order_time=30,  # Set any other required field
            status='New',
        )

    def test_my_orders_view_redirect_if_not_logged_in(self):
        response = self.client.get(reverse('customer_my_orders'))
        self.assertRedirects(response, reverse('login') + '?next=' + reverse('customer_my_orders'))

    
    def test_my_orders_view_renders_correct_template(self):
        self.client.login(username='john@example.com', password='testpass123')
        response = self.client.get(reverse('customer_my_orders'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'customers/my_orders.html')

    def test_my_orders_shows_user_orders(self):
        self.client.login(username='john@example.com', password='testpass123')
        response = self.client.get(reverse('customer_my_orders'))
        self.assertContains(response, 'My Orders')
        self.assertTrue(len(response.context['orders']) > 0)

class OrderDetailViewTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            first_name='John',
            last_name='Doe',
            username='john@example.com',
            password='testpass123'
        )
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
            is_approved=False,
            food_hub=self.food_hub
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
        
        self.order = Order.objects.create(      
            user=self.user, 
            is_ordered=True,
            order_number='12345',
            total=100.0,  # Set a valid value for the total field
            total_charge=10.0,  # Set a valid value for the total_charge field
            pre_order_time=30,  # Set any other required field
            status='New',
        )

        # Use the actual food item and user
        OrderedFood.objects.create(
            order=self.order, 
            quantity=1, 
            price=10, 
            amount=100, 
            fooditem=self.food_item,  # Correct reference to the food item
            user=self.user  # Correct reference to the user
        )

    def test_order_detail_view_renders_correct_template(self):
        self.client.login(username='john@example.com', password='testpass123')
        response = self.client.get(reverse('order_detail', kwargs={'order_number': self.order.order_number}))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'customers/order_detail.html')

    def test_order_detail_view_shows_correct_order(self):
        self.client.login(username='john@example.com', password='testpass123')
        response = self.client.get(reverse('order_detail', kwargs={'order_number': '12345'}))
        self.assertEqual(response.status_code, 200)
        self.assertIn('order', response.context)
        self.assertEqual(response.context['order'].order_number, '12345')

class OrderCancelViewTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            first_name='John',
            last_name='Doe',
            username='john@example.com',
            password='testpass123'
        )
        self.order = Order.objects.create(
            user=self.user, 
            is_ordered=True,
            order_number='12345',
            total=100.0, 
            total_charge=10.0,  # Set a valid value for the total_charge field
            pre_order_time=30,  # Set any other required field
            status='New',
        )
    def test_order_cancel_view_redirect_if_not_logged_in(self):
        response = self.client.get(reverse('order_cancel', kwargs={'order_number': '12345'}))
        expected_url = reverse('login') + '?next=' + reverse('order_cancel', kwargs={'order_number': '12345'})
        self.assertRedirects(response, expected_url)

    def test_order_cancel_success(self):
        self.client.login(username='john@example.com', password='testpass123')
        response = self.client.post(reverse('order_cancel', kwargs={'order_number': '12345'}))
        self.order.refresh_from_db()
        self.assertEqual(self.order.status, 'Cancelled')
        self.assertRedirects(response, reverse('customer_my_orders'))

    def test_order_cancel_fails_after_cutoff(self):
        self.order.created_at = timezone.now() - timedelta(hours=self.order.pre_order_time + 1)
        self.order.save()

    # Try to cancel the order
        response = self.client.post(reverse('order_cancel', kwargs={'order_number': self.order.order_number}))

    # Ensure the order status did not change to 'Cancelled'
        self.order.refresh_from_db()
        self.assertNotEqual(self.order.status, 'Cancelled')

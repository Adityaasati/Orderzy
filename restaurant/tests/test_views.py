from django.test import TestCase
from django.urls import reverse
from accounts.models import User
from menu.models import  Category, FoodItem
from orders.models import PendingOrders
from accounts.models import UserProfile
from django.contrib.messages import get_messages
from restaurant.models import FoodHub, Restaurant, OpeningHour
from django.core.files.uploadedfile import SimpleUploadedFile
import os
from django.utils.text import slugify


class RestaurantViewsTest(TestCase):

    def setUp(self):
        # Create a user and restaurant for testing
        self.user = User.objects.create_user(
            first_name='John',
            last_name='Doe',
            username='john@example.com',
            password='testpass123',
            role=1,
        )
        self.user_profile, created = UserProfile.objects.get_or_create(user=self.user)
        self.food_hub = FoodHub.objects.create(
            foodhub_name="Test Food Hub",
            latitude="12.9716",
            longitude="77.5946"
        )
        self.restaurant = Restaurant.objects.create(
            user=self.user,
            user_profile=self.user_profile,
            restaurant_name="Test Restaurant",
            is_approved=False,
            food_hub=self.food_hub
        )
        self.client.login(username='john@example.com', password='testpass123')


 
    def test_rprofile_view(self):
        """Test the restaurant profile view"""
        response = self.client.get(reverse('rprofile'))  # Testing GET request
        print(response,"response")
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'restaurant/rprofile.html')
   
        data = {
        'userprofile_field': 'some_value',  # replace with actual form field names and values
        'restaurant_field': 'some_value',
        }
        response = self.client.post(reverse('rprofile'), data, follow=True)  # Allow following the redirect
        print(response, "response 2")
        self.assertEqual(response.status_code, 200)  # After following the redirect, we expect a 200 status code
        self.assertTemplateUsed(response, 'restaurant/rprofile.html')

    def test_menu_builder_view(self):
        """Test the menu builder view"""
        response = self.client.get(reverse('menu_builder'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'restaurant/menu_builder.html')

    def test_add_category(self):
        """Test adding a category"""
        data = {
            'category_name': 'Test Category',
        }
        response = self.client.post(reverse('add_category'), data)
        self.assertEqual(response.status_code, 302)  # Should redirect after success
        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(str(messages[0]), 'Category added successfully!')

    def test_edit_category(self):
        """Test editing a category"""
        category = Category.objects.create(restaurant=self.restaurant, category_name="Test Category")
        data = {
            'category_name': 'Updated Category',
        }
        response = self.client.post(reverse('edit_category', args=[category.pk]), data)
        self.assertEqual(response.status_code, 302)  # Should redirect after success
        category.refresh_from_db()
        self.assertEqual(category.category_name, 'Updated category')

    def test_delete_category(self):
        """Test deleting a category"""
        category = Category.objects.create(restaurant=self.restaurant, category_name="Test Category")
        response = self.client.post(reverse('delete_category', args=[category.pk]))
        self.assertEqual(response.status_code, 302)  # Should redirect after deletion
        self.assertFalse(Category.objects.filter(pk=category.pk).exists())


    def test_add_food(self):
        """Test adding a food item with an image"""
    
        category = Category.objects.create(restaurant=self.restaurant, category_name="Test Category")
    
    # Construct the image path
        img_path = os.path.join(os.path.dirname(__file__), 'bg2.jpg')
        print(img_path,"img_path")
    
        with open(img_path, 'rb') as img:
            image = SimpleUploadedFile(name='bg2.jpg', content=img.read(), content_type='image/jpeg')
        
            data = {
            'food_title': 'Test Food',
            'category': category.id,
            'price': '10.00',
            'image': image,  # Include the image in the POST data
        }
        
            response = self.client.post(reverse('add_food'), data, follow=True)  # Follow the redirect
           
            
            self.assertEqual(response.status_code, 200)  # Expecting a 200 status code now
            self.assertContains(response, 'food added successfully!')  # Check if success message is present

        # Check if the image and food item were added to the page
            self.assertContains(response, 'Test Food')
            self.assertContains(response, 'Test Category')
    
    def test_edit_food(self):
        """Test editing a food item"""
        
        img_path = os.path.join(os.path.dirname(__file__), 'bg2.jpg')
        print(img_path,"img_path")
    
        with open(img_path, 'rb') as img:
            image = SimpleUploadedFile(name='bg2.jpg', content=img.read(), content_type='image/jpeg')
            category = Category.objects.create(
            restaurant=self.restaurant,
            category_name="Test Category",
            slug=slugify("Test Category"),
            description="A test category",
            )
            food = FoodItem.objects.create(
            restaurant=self.restaurant,
            category=category,
            food_title="Test Food",
            slug=slugify("Test Food"),
            description="A test food item",
            price=9.99,
            image="test_image.jpg",
            is_available=True,
            )
        
            data = {
            'food_title': 'Updated Food',
            'category': category.id,
            'price': '10.00',
            'image': image,  # Include the image in the POST data
        }

        response = self.client.post(reverse('edit_food', args=[food.pk]), data)
        self.assertEqual(response.status_code, 302)  # Should redirect after success
        food.refresh_from_db()
        print("food.food_title",food.food_title)
        self.assertEqual(food.food_title, 'Updated Food')

    def test_delete_food(self):
        """Test deleting a food item"""
        category = Category.objects.create(restaurant=self.restaurant, category_name="Test Category")
        food = FoodItem.objects.create(restaurant=self.restaurant, category=category, food_title="Test Food", price=10.00)
        response = self.client.post(reverse('delete_food', args=[food.pk]))
        self.assertEqual(response.status_code, 302)  # Should redirect after deletion
        self.assertFalse(FoodItem.objects.filter(pk=food.pk).exists())

    def test_opening_hours_view(self):
        """Test the opening hours view"""
        response = self.client.get(reverse('opening_hours'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'restaurant/opening_hours.html')

    def test_add_opening_hours(self):
        """Test adding opening hours via AJAX"""
        data = {
            'day': 1,  # Monday
            'from_hour': '09:00 AM',
            'to_hour': '05:00 PM',
            'is_closed': False,
        }
        response = self.client.post(reverse('add_opening_hours'), data, HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertEqual(response.status_code, 200)
        self.assertTrue(OpeningHour.objects.filter(restaurant=self.restaurant, day=1).exists())

    def test_remove_opening_hours(self):
        """Test removing opening hours via AJAX"""
        opening_hour = OpeningHour.objects.create(restaurant=self.restaurant, day=1, from_hour="09:00 AM", to_hour="05:00 PM")
        response = self.client.post(reverse('remove_opening_hours', args=[opening_hour.pk]), HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertEqual(response.status_code, 200)
        self.assertFalse(OpeningHour.objects.filter(pk=opening_hour.pk).exists())

    def test_my_orders_view(self):
        """Test the my orders view"""
        response = self.client.get(reverse('restaurant_my_orders'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'restaurant/my_orders.html')

    def test_pending_orders_view(self):
        """Test the pending orders view"""
        response = self.client.get(reverse('restaurant_pending_orders'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'restaurant/pending__orders.html')

    def test_seating_plan_view(self):
        """Test the seating plan view"""
        response = self.client.get(reverse('seating_plan'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'restaurant/seating_plan.html')
        
        
    def test_accept_po(self):
        """Test accepting a pending order"""
       
        pending_order,created = PendingOrders.objects.get_or_create(
        po_order_number="143",
        defaults={
            'po_is_ordered': True,
            'po_name': "Test Pending Order Rest",
            'po_total': 100.0,
            'po_order_type': "Immediate",
            'po_restaurant_id': self.restaurant.id,
            'po_num_of_people': 3,
            'po_status': 'Pending',  # Initial status should be pending
        }
    )
    
        print("created",created)
        response = self.client.post(reverse('accept_po', args=[pending_order.pk]))
        print("response",response)
        pending_order.refresh_from_db()
        self.assertEqual(pending_order.po_status, 'Accepted')

    def test_ready_po(self):
        """Test marking a pending order as ready"""
        pending_order =PendingOrders.objects.create(
            po_order_number="PEND123",
            po_is_ordered=False,
            po_name="Test Pending Order",
            po_total=100.0,
            po_order_type="Immediate",
            po_restaurant_id=self.restaurant.id,
            po_num_of_people=3
        )
        
        response = self.client.post(reverse('ready_po', args=[pending_order.pk]))
        pending_order.refresh_from_db()
        self.assertEqual(pending_order.po_status, 'Ready')

    def test_delete_po(self):
        """Test deleting a pending order"""
        pending_order = PendingOrders.objects.create(
            po_order_number="PEND123",
            po_is_ordered=False,
            po_name="Test Pending Order",
            po_total=100.0,
            po_order_type="Immediate",
            po_restaurant_id=self.restaurant.id,
            po_num_of_people=3
        )
        response = self.client.post(reverse('delete_po', args=[pending_order.pk]))
        self.assertEqual(response.status_code, 302)
        self.assertFalse(PendingOrders.objects.filter(pk=pending_order.pk).exists())

    def test_completed_po(self):
        """Test marking a pending order as completed"""
        pending_order = PendingOrders.objects.create(
            po_order_number="PEND123",
            po_is_ordered=False,
            po_name="Test Pending Order",
            po_total=100.0,
            po_order_type="Immediate",
            po_restaurant_id=self.restaurant.id,
            po_num_of_people=3
        )
        response = self.client.post(reverse('completed_po', args=[pending_order.pk]))
        pending_order.refresh_from_db()
        self.assertEqual(pending_order.po_status, 'Completed')



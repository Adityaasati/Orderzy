
from django.test import TestCase
from django.urls import reverse
from orders.models import   Order, PendingOrders
from accounts.models import UserProfile,User
from menu.models import  Category, FoodItem
from restaurant.models import Restaurant, OpeningHour,FoodHub
from django.utils.text import slugify



class RestaurantURLsTest(TestCase):
    
    def setUp(self):
        self.user = User.objects.create_user(
            first_name='John',
            last_name='Doe',
            username='john@example.com',
            password='testpass123',
        )
        self.user.role=1
        self.user.save()
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
            is_approved=True,
            food_hub=self.food_hub
        )
        self.category = Category.objects.create(restaurant=self.restaurant, category_name="Test Category")
        
        self.food = FoodItem.objects.create(
            restaurant=self.restaurant,
            category=self.category,
            food_title="Test Food",
            slug=slugify("Test Food"),
            description="A test food item",
            price=9.99,
            image="test_image.jpg",
            is_available=True,
            )
        self.opening_hour = OpeningHour.objects.create(restaurant=self.restaurant, day=1, from_hour="09:00 AM", to_hour="05:00 PM")
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
        self.pending_order = PendingOrders.objects.create(
            po_order_number="PEND123",
            po_is_ordered=False,
            po_name="Test Pending Order",
            po_total=100.0,
            po_order_type="Immediate",
            po_restaurant_id=self.restaurant.id,
            po_num_of_people=3
        )
        self.client.login(username='john@example.com', password='testpass123')

    def test_restaurant_dashboard_url(self):
        url = reverse('restaurant')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_profile_url(self):
        url = reverse('rprofile')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_menu_builder_url(self):
        url = reverse('menu_builder')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_fooditems_by_category_url(self):
        url = reverse('fooditems_by_category', args=[self.category.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    # CRUD tests for Category
    def test_add_category_url(self):
        url = reverse('add_category')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_edit_category_url(self):
        url = reverse('edit_category', args=[self.category.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_delete_category_url(self):
        url = reverse('delete_category', args=[self.category.id])
        response = self.client.post(url)
        self.assertEqual(response.status_code, 302)  # Assuming deletion redirects

    # CRUD tests for Food Items
    def test_add_food_url(self):
        url = reverse('add_food')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_edit_food_url(self):
        url = reverse('edit_food', args=[self.food.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_delete_food_url(self):
        url = reverse('delete_food', args=[self.food.id])
        response = self.client.post(url)
        self.assertEqual(response.status_code, 302)

    # CRUD tests for Opening Hours
    def test_opening_hours_url(self):
        url = reverse('opening_hours')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_add_opening_hours_url(self):
        url = reverse('add_opening_hours')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_remove_opening_hours_url(self):
        print(self.user,self.user.role, self.user.username, self.restaurant)
        opening_hour = OpeningHour.objects.create(
        restaurant=self.restaurant, 
        day=1, 
        from_hour='09:00', 
        to_hour='18:00'
    )
    
        url = reverse('remove_opening_hours', args=[opening_hour.id])
    
        response = self.client.post(url, {}, HTTP_X_REQUESTED_WITH='XMLHttpRequest')
    
        self.assertEqual(response.status_code, 200)
        self.assertJSONEqual(response.content, {'status': 'success', 'id': opening_hour.id})


    # Order tests
    def test_order_detail_url(self):
        url = reverse('restaurant_order_detail', args=[self.order.order_number])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_my_orders_url(self):
        url = reverse('restaurant_my_orders')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    # Pending Orders and Actions
    def test_pending_orders_url(self):
        url = reverse('restaurant_pending_orders')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_accept_pending_order_url(self):
        url = reverse('accept_po', args=[self.pending_order.id])
        response = self.client.post(url)
        self.assertEqual(response.status_code, 302)  # Assuming a redirect after acceptance

    def test_ready_pending_order_url(self):
        url = reverse('ready_po', args=[self.pending_order.id])
        response = self.client.post(url)
        self.assertEqual(response.status_code, 302)

    def test_completed_pending_order_url(self):
        url = reverse('completed_po', args=[self.pending_order.id])
        response = self.client.post(url)
        self.assertEqual(response.status_code, 302)

    def test_delete_pending_order_url(self):
        url = reverse('delete_po', args=[self.pending_order.id])
        response = self.client.post(url)
        self.assertEqual(response.status_code, 302)

    # Seating Plan Tests
    def test_seating_plan_url(self):
        url = reverse('seating_plan')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

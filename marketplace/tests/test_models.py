from django.test import TestCase
from accounts.models import User
from menu.models import FoodItem,Category
from marketplace.models import Cart, Service_Charge
from django.utils import timezone
from accounts.models import User,UserProfile
from restaurant.models import FoodHub,Restaurant
from django.utils.text import slugify
from django.core.files.uploadedfile import SimpleUploadedFile


class CartModelTest(TestCase):
    
    def setUp(self):
        # Create a test user and food item

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
        

    def test_create_cart(self):
        # Create a Cart object
        cart = Cart.objects.create(user=self.user, fooditem=self.food_item, quantity=2)
        
        # Check that the cart item is created successfully
        self.assertEqual(cart.user, self.user)
        self.assertEqual(cart.fooditem, self.food_item)
        self.assertEqual(cart.quantity, 2)
        self.assertIsNotNone(cart.created_at)  # Auto-generated fields
        self.assertIsNotNone(cart.updated_at)

    def test_cart_unicode_representation(self):
        cart = Cart.objects.create(user=self.user, fooditem=self.food_item, quantity=1)
        self.assertEqual(str(cart), str(self.user))

    def test_cart_quantity_positive(self):
        # Ensure that the quantity is a positive integer
        cart = Cart.objects.create(user=self.user, fooditem=self.food_item, quantity=5)
        self.assertGreater(cart.quantity, 0)

    def test_cart_auto_timestamps(self):
        # Ensure that created_at and updated_at are set automatically
        cart = Cart.objects.create(user=self.user, fooditem=self.food_item, quantity=1)
        self.assertIsNotNone(cart.created_at)
        self.assertIsNotNone(cart.updated_at)
        self.assertTrue(cart.created_at <= timezone.now())
        self.assertTrue(cart.updated_at <= timezone.now())


class ServiceChargeModelTest(TestCase):

    def test_create_service_charge(self):
        # Create a Service_Charge object
        service_charge = Service_Charge.objects.create(
            service_charge_type='Test Service',
            service_charge_percentage=10.00
        )
        
        # Check that the service charge was created successfully
        self.assertEqual(service_charge.service_charge_type, 'Test Service')
        self.assertEqual(service_charge.service_charge_percentage, 10.00)
        self.assertTrue(service_charge.is_active)

    def test_service_charge_type_unique(self):
        # Create a Service_Charge object
        Service_Charge.objects.create(
            service_charge_type='Test Service',
            service_charge_percentage=10.00
        )
        
        # Attempt to create another Service_Charge with the same type should raise an IntegrityError
        with self.assertRaises(Exception):
            Service_Charge.objects.create(
                service_charge_type='Test Service',  # Duplicate type
                service_charge_percentage=15.00
            )

    def test_service_charge_percentage_valid(self):
        # Ensure service charge accepts valid decimal values
        service_charge = Service_Charge.objects.create(
            service_charge_type='Another Service',
            service_charge_percentage=12.34
        )
        self.assertEqual(service_charge.service_charge_percentage, 12.34)

    def test_service_charge_is_active_default(self):
        # Ensure the default value of is_active is True
        service_charge = Service_Charge.objects.create(
            service_charge_type='Another Service',
            service_charge_percentage=5.00
        )
        self.assertTrue(service_charge.is_active)

    def test_service_charge_string_representation(self):
        # Ensure that __str__ method returns the service_charge_type
        service_charge = Service_Charge.objects.create(
            service_charge_type='Express Service',
            service_charge_percentage=5.00
        )
        self.assertEqual(str(service_charge), 'Express Service')

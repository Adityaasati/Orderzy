from django.test import TestCase
from django.urls import reverse
from accounts.models import User,UserProfile
from marketplace.models import Cart
from restaurant.models import Restaurant,FoodHub
from menu. models import Category,FoodItem
from django.utils.text import slugify
from django.core.files.uploadedfile import SimpleUploadedFile

class URLTests(TestCase):
    
    def test_home_url(self):
        """Test home page URL"""
        response = self.client.get(reverse('home'))
        self.assertEqual(response.status_code, 200)
    
    def test_base_url(self):
        """Test base page URL"""
        response = self.client.get(reverse('base'))
        self.assertEqual(response.status_code, 200)
    
    def test_accounts_urls(self):
        """Test the inclusion of accounts URLs"""
        # Assuming the accounts app has a login view
        response = self.client.get(reverse('login'))
        self.assertEqual(response.status_code, 200)



    
    def test_admin_url(self):
        """Test admin URL"""
        response = self.client.get('/admin/')
        self.assertEqual(response.status_code, 302)  # Admin usually redirects to login page
        
        


class MarketplaceURLsTest(TestCase):
    def setUp(self):
        # Create a test user and log them in
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
        self.client.login(username='john@example.com', password='testpass123')

    def test_cart_url(self):
        """Test cart page URL"""
        response = self.client.get(reverse('cart'))
        self.assertEqual(response.status_code, 200)

    def test_search_url(self):
        """Test search page URL"""
        response = self.client.get(reverse('search'))
        self.assertEqual(response.status_code, 200)

    def test_checkout_url_with_empty_cart(self):
        """Test checkout URL with an empty cart"""
        response = self.client.get(reverse('checkout'))

        # Check if redirected to marketplace due to empty cart
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('marketplace'))

    def test_checkout_url_with_cart_items(self):
        """Test checkout URL with items in the cart"""
        # Add items to the cart
        Cart.objects.create(user=self.user, fooditem=self.food_item, quantity=2)  # Adjust fields according to your Cart model

        response = self.client.get(reverse('checkout'))

        # Ensure no redirection happens when the cart is not empty
        self.assertEqual(response.status_code, 200)
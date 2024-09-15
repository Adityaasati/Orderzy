from django.test import TestCase
from django.urls import reverse
from marketplace.models import Cart, Service_Charge
from menu.models import FoodItem, Category
from restaurant.models import FoodHub, Restaurant
from accounts.models import UserProfile,User
from orders.forms import OrderForm
from django.core.files.uploadedfile import SimpleUploadedFile
from django.utils.text import slugify



class MarketplaceTestCase(TestCase):

    def setUp(self):
        # Create user and related profile
        self.user = User.objects.create_user(
            first_name='John',
            last_name='Doe',
            username='john@example.com',
            password='testpassword',
            is_active = True
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
            is_approved=True,
            food_hub=self.food_hub
        )
        

        # Create category and food item
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

    ### Test `marketplace` View ###
    def test_marketplace_view(self):
        response = self.client.get(reverse('marketplace'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'marketplace/listings.html')
        self.assertIn('restaurants', response.context)
        self.assertEqual(response.context['restaurant_count'], 1)  # Ensure only 1 restaurant

    ### Test `restaurant_detail` View ###
    def test_restaurant_detail_view(self):
        response = self.client.get(reverse('restaurant_detail', args=[self.restaurant.restaurant_slug]))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'marketplace/restaurant__detail.html')
        self.assertIn('categories', response.context)

    ### Test `add_to_cart` View ###
    def test_add_to_cart_authenticated_user(self):
        self.client.login(username='john@example.com', password='testpassword')
        response = self.client.post(reverse('add_to_cart', args=[self.food_item.id]), HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Cart.objects.filter(user=self.user).count(), 1)  # Ensure item is added to cart

    def test_add_to_cart_invalid_food(self):
        self.client.login(username='john@example.com', password='testpassword')
        response = self.client.post(reverse('add_to_cart', args=[9999]), HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertEqual(response.status_code, 200)
        self.assertJSONEqual(response.content, {'status': 'Failed', 'message': 'This food item does not exist'})

    ### Test `decrease_cart` View ###
    def test_decrease_cart(self):
        cart_item = Cart.objects.create(user=self.user, fooditem=self.food_item, quantity=2)
        self.client.login(username='john@example.com', password='testpassword')
        response = self.client.post(reverse('decrease_cart', args=[self.food_item.id]), HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertEqual(response.status_code, 200)
        cart_item.refresh_from_db()
        self.assertEqual(cart_item.quantity, 1)

    def test_decrease_cart_remove_item(self):
        cart_item = Cart.objects.create(user=self.user, fooditem=self.food_item, quantity=1)
        self.client.login(username='john@example.com', password='testpassword')
        response = self.client.post(reverse('decrease_cart', args=[self.food_item.id]), HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Cart.objects.filter(user=self.user).count(), 0)  # Item should be removed from cart

    ### Test `cart` View ###
    def test_cart_view(self):
        Cart.objects.create(user=self.user, fooditem=self.food_item, quantity=1)
        self.client.login(username='john@example.com', password='testpassword')
        response = self.client.get(reverse('cart'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'marketplace/cart.html')
        self.assertIn('cart_items', response.context)


    def test_delete_cart(self):
        cart_item = Cart.objects.create(user=self.user, fooditem=self.food_item, quantity=1)
        self.client.login(username='john@example.com', password='testpassword')
        response = self.client.post(reverse('delete_cart', args=[cart_item.id]), HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Cart.objects.filter(user=self.user).count(), 0)

    ### Test `search` View ###
    def test_search_view(self):
        response = self.client.get(reverse('search'), {'keyword': 'Test'})
        self.assertEqual(response.status_code, 200)
        self.assertIn('restaurants', response.context)

    ### Test `checkout` View ###
    def test_checkout_view(self):
        Cart.objects.create(user=self.user, fooditem=self.food_item, quantity=1)
        self.client.login(username='john@example.com', password='testpassword')
        response = self.client.get(reverse('checkout'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'marketplace/checkout.html')
        self.assertIn('form', response.context)
        self.assertIn('cart_items_with_totals', response.context)
        self.assertEqual(response.context['cart_count'], 1)

    def test_checkout_redirect_empty_cart(self):
        self.client.login(username='john@example.com', password='testpassword')
        response = self.client.get(reverse('checkout'))
        self.assertEqual(response.status_code, 302)  # Redirect to marketplace
        self.assertRedirects(response, reverse('marketplace'))


from django.test import TestCase
from django.utils.text import slugify
from menu.models import Category, FoodItem
from accounts.models import UserProfile,User
from restaurant.models import Restaurant,FoodHub
from menu.models import FoodItem,Category
from restaurant.models import Restaurant,FoodHub
from django.core.files.uploadedfile import SimpleUploadedFile

class CategoryModelTest(TestCase):

    def setUp(self):
        
        self.user = User.objects.create_user(
            username='john@example.com',
            password='testpass123',
            first_name='John',
            last_name='Doe'
        )
        self.user.role = 1
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
            category_name="Test category",
            slug="test-category",
            description="A test category",
        )

    def test_category_creation(self):
        """Test if the Category is created properly"""
        self.assertEqual(self.category.category_name, "Test category")
        self.assertEqual(self.category.slug, "test-category")
        self.assertEqual(self.category.restaurant, self.restaurant)

    def test_category_str(self):
        """Test the string representation of the Category model"""
        self.assertEqual(str(self.category), "Test category")

    def test_category_clean(self):
        """Test if the clean method capitalizes category_name"""
        category = Category.objects.create(
            restaurant=self.restaurant,
            category_name="lowercase category",
            slug=slugify("lowercase category"),
            description="Another test category",
        )
        category.clean()  # Calling the clean method
        self.assertEqual(category.category_name, "Lowercase category")

    def test_category_meta(self):
        """Test the verbose name and plural of the Category model"""
        self.assertEqual(self.category._meta.verbose_name, 'category')
        self.assertEqual(self.category._meta.verbose_name_plural, 'categories')


class FoodItemModelTest(TestCase):

    def setUp(self):
        # Create a Restaurant and Category instance
        self.user = User.objects.create_user(
            username='john@example.com',
            password='testpass123',
            first_name='John',
            last_name='Doe'
        )
        self.user.role = 1
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
            price=9.99,
            category=self.category,
            restaurant=self.restaurant,
            image=SimpleUploadedFile("test.jpg", b"file_content", content_type="image/jpeg")
        )

    def test_fooditem_creation(self):
        """Test if the FoodItem is created properly"""
        self.assertEqual(self.food_item.food_title, "Test Food")
        self.assertEqual(self.food_item.slug, "test-food")
        self.assertEqual(self.food_item.price, 9.99)
        self.assertTrue(self.food_item.is_available)

    def test_fooditem_str(self):
        """Test the string representation of the FoodItem model"""
        self.assertEqual(str(self.food_item), "Test Food")

    def test_fooditem_default_is_available(self):
        """Test the default value of is_available"""
        new_food_item = FoodItem.objects.create(
            restaurant=self.restaurant,
            category=self.category,
            food_title="Another Test Food",
            slug=slugify("Another Test Food"),
            description="Another test food item",
            price=14.99,
            image="test_image2.jpg",
        )
        self.assertTrue(new_food_item.is_available)

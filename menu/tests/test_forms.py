from django.test import TestCase
from django.core.files.uploadedfile import SimpleUploadedFile
from menu.forms import CategoryForm, FoodItemForm
from menu.models import Category, Restaurant
from accounts.validators import allow_only_images_validator
from django.core.exceptions import ValidationError
from accounts.models import UserProfile,User
from restaurant.models import Restaurant,FoodHub
from menu.models import FoodItem,Category

class FormTests(TestCase):

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
            category_name="Test Category",
            slug="test-category",
            description="A test category",
        )
    

    
    def test_category_form_valid_data(self):
        form = CategoryForm(data={
            'category_name': 'Main Course',
            'description': 'Main Course description',
        })
        self.assertTrue(form.is_valid())  # Ensure form is valid
    
    def test_category_form_missing_data(self):
        form = CategoryForm(data={})
        self.assertFalse(form.is_valid())  # Ensure form is invalid
        self.assertIn('category_name', form.errors)  # Ensure 'category_name' is required
    
    ### FoodItemForm Tests ###
    
    def test_fooditem_form_valid_data(self):
        image = SimpleUploadedFile("bg2.jpg", b"file_content", content_type="image/jpeg")
        form = FoodItemForm(data={
            'category': self.category.id,
            'food_title': 'Test Food',
            'description': 'Delicious test food',
            'price': 10.99,
            'is_available': True,
        }, files={'image': image})
        self.assertTrue(form.is_valid())  # Ensure form is valid

    def test_fooditem_form_missing_data(self):
        form = FoodItemForm(data={})
        self.assertFalse(form.is_valid())  # Ensure form is invalid
        self.assertIn('category', form.errors)  # Ensure 'category' is required
        self.assertIn('food_title', form.errors)  # Ensure 'food_title' is required
        self.assertIn('price', form.errors)  # Ensure 'price' is required

    def test_fooditem_form_invalid_image_file(self):
        # Test the form with a non-image file
        invalid_file = SimpleUploadedFile("test.txt", b"file_content", content_type="text/plain")
        form = FoodItemForm(data={
            'category': self.category.id,
            'food_title': 'Test Food',
            'description': 'Delicious test food',
            'price': 10.99,
            'is_available': True,
        }, files={'image': invalid_file})

        self.assertFalse(form.is_valid())  # Ensure form is invalid due to invalid image
        self.assertIn('image', form.errors)  # Check that the 'image' field has errors
        self.assertEqual(form.errors['image'][0], "Unsupported file extension. Allowed extensions are ['.png', '.jpg', '.jpeg']")

    def test_fooditem_form_missing_image(self):
        # Test the form without an image
        form = FoodItemForm(data={
            'category': self.category.id,
            'food_title': 'Test Food',
            'description': 'Delicious test food',
            'price': 10.99,
            'is_available': True,
        })

        self.assertTrue(form.is_valid())  # Ensure form is valid even without an image (assuming image is optional)


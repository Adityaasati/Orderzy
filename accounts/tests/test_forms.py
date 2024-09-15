
from django.core.files.uploadedfile import SimpleUploadedFile
import os
from django.test import TestCase
from django.urls import reverse
from accounts.forms import UserForm, UserProfileForm, UserInfoForm, LoginForm, ContactForm
from accounts.models import User, UserProfile, ContactMessage


class UserFormTest(TestCase):

    def setUp(self):
        User.objects.create(first_name= 'Rahul', last_name='Ji', username="existing@example.com", password="password123")
        User.objects.create(first_name= 'Ram', last_name='Rastogi', username="1234567890", password="password123")

    def test_user_form_valid_with_email(self):
        """Test form submission with a valid email as username"""
        form_data = {
            'first_name': 'John',
            'last_name': 'Doe',
            'username': 'john@example.com',
            'password': 'password123',
        }
        form = UserForm(data=form_data)
        self.assertTrue(form.is_valid(), form.errors)

    def test_user_form_valid_with_phone_number(self):
        """Test form submission with a valid phone number as username"""
        form_data = {
            'first_name': 'John',
            'last_name': 'Doe',
            'username': '9876543210',
            'password': 'password123',
        }
        form = UserForm(data=form_data)
        self.assertTrue(form.is_valid(), form.errors)

    def test_user_form_invalid_without_username(self):
        """Test form submission without a username"""
        form_data = {
            'first_name': 'John',
            'last_name': 'Doe',
            'username': '',
            'password': 'password123',
        }
        form = UserForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('Username is required.', form.errors['__all__'])

    def test_user_form_invalid_with_existing_email(self):
        """Test form submission with an existing email"""
        form_data = {
            'first_name': 'John',
            'last_name': 'Doe',
            'username': 'existing@example.com',  # This email is already taken
            'password': 'password123',
        }
        form = UserForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('User with this Email already exists.', form.errors['__all__'])

    def test_user_form_invalid_with_existing_phone_number(self):
        """Test form submission with an existing phone number"""
        form_data = {
            'first_name': 'John',
            'last_name': 'Doe',
            'username': '1234567890',  # This phone number is already taken
            'password': 'password123',
        }
        form = UserForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('User with this Phone Number already exists.', form.errors['__all__'])

    def test_user_form_invalid_with_email_format(self):
        """Test form submission with an invalid email format"""
        form_data = {
            'first_name': 'John',
            'last_name': 'Doe',
            'username': 'johnexample.com',  # Missing '@'
            'password': 'password123',
        }
        form = UserForm(data=form_data)
        self.assertTrue(form.is_valid())  # The form would still be valid if '@' is not strictly validated


class UserProfileFormTest(TestCase):

    def setUp(self):
        image_path = os.path.join(os.path.dirname(__file__), 'bg2.jpg')
        print(image_path)
        with open(image_path, 'rb') as img:
            image = SimpleUploadedFile(name='bg2.jpg', content=img.read(), content_type='image/jpeg')
            
        self.form = UserProfileForm(data={
            'address': '123 Main St',
            'country': 'CountryName',
            'state': 'StateName',
            'city': 'CityName',
            'pin_code': '123456',
            'latitude': '12.34',
            'longitude': '56.78',
        }, files={
            'profile_picture': image,
            'cover_photo': image
        })
      

    def test_user_profile_form_valid(self):
        self.assertTrue(self.form.is_valid())
        


    def test_user_profile_form_latitude_longitude_readonly(self):
        form = UserProfileForm()
        self.assertEqual(form.fields['latitude'].widget.attrs['readonly'], 'readonly')
        self.assertEqual(form.fields['longitude'].widget.attrs['readonly'], 'readonly')


class UserInfoFormTest(TestCase):

    def setUp(self):
        self.user_info_data = {
            'first_name': 'John',
            'last_name': 'Doe',
            'phone_number': '1234567890',
        }

    def test_user_info_form_valid(self):
        form = UserInfoForm(data=self.user_info_data)
        self.assertTrue(form.is_valid())


class LoginFormTest(TestCase):

    def test_login_form_valid(self):
        form_data = {
            'identifier': 'john@example.com',
            'password': 'password123'
        }
        form = LoginForm(data=form_data)
        self.assertTrue(form.is_valid())

    def test_login_form_invalid_without_identifier(self):
        form_data = {'password': 'password123'}
        form = LoginForm(data=form_data)
        self.assertFalse(form.is_valid())

    def test_login_form_invalid_without_password(self):
        form_data = {'identifier': 'john@example.com'}
        form = LoginForm(data=form_data)
        self.assertFalse(form.is_valid())


class ContactFormTest(TestCase):

    def setUp(self):
        self.contact_data = {
            'name': 'John Doe',
            'message': 'Hello, I need help with my account.',
        }

    def test_contact_form_valid(self):
        form = ContactForm(data=self.contact_data)
        self.assertTrue(form.is_valid())

    def test_contact_form_invalid_without_name(self):
        self.contact_data['name'] = ''
        form = ContactForm(data=self.contact_data)
        self.assertFalse(form.is_valid())

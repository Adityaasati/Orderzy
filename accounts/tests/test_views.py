from django.test import TestCase
from django.urls import reverse
from django.shortcuts import redirect

from accounts.models import User, UserProfile
from restaurant.models import Restaurant
from orders.models import Order
from django.conf import settings

class RegisterUserViewTest(TestCase):

    def test_register_user_valid_data(self):
        """
        Test the registerUser view with valid form data and successful user creation.
        """
        valid_data = {
            'first_name': 'John',
            'last_name': 'Doe',
            'username': 'john_doe',
            'email': 'john@example.com',
            'password': 'password123',
        }
        response = self.client.post(reverse('registerUser'), data=valid_data)

        # Expect a redirect to the login page after successful registration
        self.assertRedirects(response, reverse('login'))

        # Ensure the user was created
      

    def test_register_user_invalid_data(self):
        """
        Test the registerUser view with invalid form data (e.g., missing username).
        """
        invalid_data = {
            'first_name': 'John',
            'last_name': 'Doe',
            'email': 'john@example.com',
            'password': 'password123',
            # Missing 'username' and 'phone_number'
        }
        response = self.client.post(reverse('registerUser'), data=invalid_data)
        
        # Should not redirect, should stay on the registration page with errors
        self.assertEqual(response.status_code, 200)

        form = response.context['form']
        self.assertTrue(form.errors)
        
        # Check for field-specific error for 'username'
        self.assertIn('username', form.errors)
        self.assertEqual(form.errors['username'], ['This field is required.'])

        # Check for non-field error
        self.assertIn('__all__', form.errors)
        self.assertEqual(form.errors['__all__'], ['Username is required.'])


class LoginViewTest(TestCase):
    def setUp(self):
        # Create a test user with first_name and last_name
        self.user = User.objects.create_user(
            username='testuser',
            password='password123',
            first_name='John',
            last_name='Doe',
            email='testuser@example.com',
            is_active=True
        )

    def test_login_view_get(self):
        """
        Test that the login view renders the correct template on GET request.
        """
        response = self.client.get(reverse('login'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'accounts/login.html')

    def test_login_valid_credentials(self):
        """
        Test logging in with valid credentials.
        """
        response = self.client.post(reverse('login'), {
            'identifier': 'testuser',
            'password': 'password123',
        })
        print(f"Response status code: {response.status_code}")  # Debugging
    
        self.assertRedirects(response, reverse('marketplace'))

    def test_login_invalid_credentials(self):
        """
        Test logging in with invalid credentials.
        """
        response = self.client.post(reverse('login'), {
            'identifier': 'non_existent_user',
            'password': 'wrongpassword',
        })
        self.assertContains(response, 'Invalid credentials')

    def test_redirect_view(request):
        return redirect('marketplace')

class CustomerDashboardViewTest(TestCase):
    def setUp(self):
        # Create a test user with first_name and last_name
        self.user = User.objects.create_user(
            username='testuser',
            password='password123',
            first_name='John',
            last_name='Doe',
            role=User.CUSTOMER
        )
        self.client.login(username='testuser', password='password123')

    def test_customer_dashboard(self):
        """
        Test that the customer dashboard is accessible for a logged-in customer.
        """
        response = self.client.get(reverse('custDashboard'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'accounts/custDashboard.html')




# User = get_user_model()

class RegisterRestaurantViewTest(TestCase):

    def setUp(self):
        self.register_url = reverse('registerRestaurant')

    def test_register_restaurant_valid_data(self):
        response = self.client.post(self.register_url, {
            'first_name': 'John',
            'last_name': 'Doe',
            'username': 'john_doe',
            'email': 'john@example.com',
            'password': 'password123',
            'restaurant_name': 'Test Restaurant'
        })

        # Check that it redirects to the correct URL
        self.assertRedirects(response, reverse('registerRestaurant'))

    def test_register_restaurant_invalid_user_form(self):
        response = self.client.post(self.register_url, {
            'last_name': 'Doe',
            'username': 'john_doe',
            'email': 'john@example.com',
            'password': 'password123',
            'restaurant_name': 'Test Restaurant'
        })

        # Ensure the form is available in the response context
        form = response.context.get('form')
        self.assertIsNotNone(form)

        # Should display form errors
        self.assertEqual(response.status_code, 200)
        self.assertFormError(form, 'first_name', 'This field is required.')

    def test_register_restaurant_invalid_restaurant_form(self):
        response = self.client.post(self.register_url, {
            'first_name': 'John',
            'last_name': 'Doe',
            'username': 'john_doe',
            'email': 'john@example.com',
            'password': 'password123',
            'restaurant_name': ''  # Invalid restaurant name
        })

        # Ensure the restaurant form is available in the response context
        r_form = response.context.get('r_form')
        self.assertIsNotNone(r_form)

        self.assertEqual(response.status_code, 200)
        self.assertFormError(r_form, 'restaurant_name', 'This field is required.')

class RestaurantDashboardViewTest(TestCase):

    def setUp(self):
        self.non_restaurant_user = User.objects.create_user(
            first_name='John', last_name='Doe',
            username='testuser', 
            password='testpassword'
        )
        self.non_restaurant_user.role = 2  # Assuming role 2 is for a non-restaurant user
        self.non_restaurant_user.save()



    def test_dashboard_access_denied_for_non_restaurant_user(self):
        self.client.login(username='testuser', password='testpassword')

        response = self.client.get(reverse('restaurantDashboard'))

        self.assertEqual(response.status_code, 403)

        self.assertEqual(response.status_code, 403)

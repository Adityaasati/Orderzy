
from django.core import mail
from django.test import TestCase
from django.urls import reverse
from django.test import Client
from accounts.models import User, UserProfile
from restaurant.models import FoodHub, Restaurant
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes


class UrlsTestCase(TestCase):

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            first_name='Test',
            last_name='User',
            username='testuser@example.com',
            password='password123',
            is_active=True,
            
        )
        self.user.role = 2  # Assign a role (e.g., 1 for restaurant)
        self.user.save() 
        
        self.user2 = User.objects.create_user(
            first_name='Test',
            last_name='restaurant',
            username='restaurantnew3@example.com',
            password='password123',
            is_active=False,
            
        )
        self.user2.role = 1  
        self.user2.save() 
        
        self.profile, created = UserProfile.objects.get_or_create(user=self.user2)
        self.food_hub = FoodHub.objects.create(
            foodhub_name="Test Food Hub",
            latitude="12.9716",
            longitude="77.5946"
        )
        self.restaurant = Restaurant.objects.create(
            user=self.user2,
            user_profile=self.profile,
            restaurant_name="Test Restaurant",
            food_hub=self.food_hub,
            is_approved=False,
       
        )
        self.user3 = User.objects.create_user(
            first_name='Test',
            last_name='User',
            username='+9123678905',
            password='password123',
            is_active=True,
            
        )
        self.user3.role = 2  # Assign a role (e.g., 1 for restaurant)
        self.user3.save()
        
        self.uidb64 = urlsafe_base64_encode(force_bytes(self.user2.pk))
        self.token = default_token_generator.make_token(self.user2)

    def test_register_user_url(self):
        """Test user registration URL and view."""
        response = self.client.get(reverse('registerUser'))
        self.assertEqual(response.status_code, 200)
        
        response = self.client.post(reverse('registerUser'), {
            'first_name': 'John',
            'last_name': 'Doe',
            'username': 'johndoe@example.com',
            'password': 'password123',
        })
        self.assertEqual(response.status_code, 302)  # Should redirect after successful registration

    def test_register_restaurant_url(self):
        """Test restaurant registration URL and view."""
        response = self.client.get(reverse('registerRestaurant'))
        self.assertEqual(response.status_code, 200)
        
        response = self.client.post(reverse('registerRestaurant'), {
            'first_name': 'Rest',
            'last_name': 'Owner',
            'username': 'rest@example.com',
            'password': 'password123',
            'restaurant_name': 'My Test Restaurant',
        })

        self.assertEqual(response.status_code, 302)  # Should redirect after successful registration

    def test_login_url(self):
        """Test login URL and view."""
        response = self.client.get(reverse('login'))
        self.assertEqual(response.status_code, 200)

        # Test login with correct credentials
        response = self.client.post(reverse('login'), {
        'identifier': 'testuser@example.com',  # Use 'identifier' as the form expects
        'password': 'password123'
    })
        if response.status_code == 200:
            print("Form fields:", response.context['form'].fields)
            print("Form errors:", response.context['form'].errors)

        self.assertEqual(response.status_code, 302)  # Redirect to account page

    def test_logout_url(self):
        """Test logout URL."""
        self.client.login(username='testuser@example.com', password='password123')
        response = self.client.get(reverse('logout'))
        self.assertEqual(response.status_code, 302)  # Redirect after logout

    def test_my_account_url(self):
        """Test my account URL and view."""
        login_successful = self.client.login(username=self.user2.username, password='password123')
        self.assertTrue(login_successful, "Login should be successful")

        response = self.client.get(reverse('myAccount'))

        self.assertEqual(response.status_code, 302)  
        self.assertEqual(response.url, reverse('restaurantDashboard'))  
        
        
    def test_cust_dashboard_url(self):
        """Test customer dashboard URL and view."""
        self.client.login(username='testuser@example.com', password='password123')
        response = self.client.get(reverse('custDashboard'))
        
        self.assertEqual(response.status_code, 200)

    def test_restaurant_dashboard_url(self):
        """Test restaurant dashboard URL and view."""
        
        self.client.login(username='restaurantnew3@example.com', password='password123')
        response = self.client.get(reverse('restaurantDashboard'))
        self.assertEqual(response.status_code, 200)

    def test_activate_account_valid(self):
        """Test activating an account with a valid token and user ID."""
        print(f"Generated token in test: {self.token}")
        print(f"User is active before activation: {self.user2.is_active}")
    
    # **Remove the unnecessary login attempt**
    # self.client.login(username=self.user2.username, password='password123')
    
    # Perform activation
        response = self.client.get(
        reverse('activate', kwargs={'uidb64': self.uidb64, 'token': self.token}),
        follow=True
    )
    
    # Refresh user2 from the database to get updated is_active status
        self.user2.refresh_from_db()  
        print(f"User is active after activation: {self.user2.is_active}")
    
    # **Check if the user is now active**
        self.assertTrue(self.user2.is_active)  
    
    # **Check the response status code**
        self.assertEqual(response.status_code, 200) 
    
    # **Verify redirection based on user role**
        if self.user2.role == 1: 
            self.assertRedirects(response, reverse('restaurantDashboard'))  # Check if it redirects to the restaurant dashboard
        else:
            self.assertRedirects(response, reverse('custDashboard'))

    def test_activate_account_invalid_token(self):
        """Test activating an account with an invalid token."""
        invalid_token = 'invalid-token'
    
        response = self.client.get(reverse('activate', kwargs={'uidb64': self.uidb64, 'token': invalid_token}), follow=True)

        self.user2.refresh_from_db()

        self.assertFalse(self.user2.is_active) 

        self.assertRedirects(response, '/login/?next=/myAccount/', status_code=302)  # Redirect to login page

    def test_activate_account_invalid_uid(self):
        """Test activating an account with an invalid UID."""
        invalid_uidb64 = 'invalid-uid'
        response = self.client.get(reverse('activate', kwargs={'uidb64': invalid_uidb64, 'token': self.token}), follow=True)

        self.user2.refresh_from_db()
        self.assertFalse(self.user2.is_active)  

        self.assertRedirects(response, '/login/?next=/myAccount/', status_code=302)  




    def test_forgot_password_valid_email(self):
        """Test when a valid email is provided and user exists."""
        response = self.client.post(reverse('forgot_password'), {'identifier': 'testuser@example.com'})

        self.assertRedirects(response, reverse('login'))
        messages = list(response.wsgi_request._messages)
        self.assertEqual(str(messages[0]), 'Password reset link has been sent to your email.')

        self.assertEqual(len(mail.outbox), 1)
        self.assertIn('Reset Your Password', mail.outbox[0].subject)

    def test_forgot_password_non_existent_email(self):
        """Test when a valid email is provided but user doesn't exist."""
        response = self.client.post(reverse('forgot_password'), {'identifier': 'nonexistent@example.com'})
        
        self.assertRedirects(response, reverse('forgot_password'))
        messages = list(response.wsgi_request._messages)
        self.assertEqual(str(messages[0]), 'Account does not exist.')

        # Ensure no email is sent
        self.assertEqual(len(mail.outbox), 0)

    def test_forgot_password_invalid_email(self):
        """Test when an invalid email is provided."""
        response = self.client.post(reverse('forgot_password'), {'identifier': 'invalid-email'})
        
        # Ensure the error message is displayed
        self.assertRedirects(response, reverse('forgot_password'))
        messages = list(response.wsgi_request._messages)
        self.assertEqual(str(messages[0]), 'Please enter a valid email address or phone number.')

        # Ensure no email is sent
        self.assertEqual(len(mail.outbox), 0)

    def test_forgot_password_valid_phone(self):
        """Test when a valid phone number is provided and user exists."""
        response = self.client.post(reverse('forgot_password'), {'identifier': '+9123678905'})

        # Ensure the success message is displayed
        self.assertRedirects(response, reverse('login'))
        messages = list(response.wsgi_request._messages)
        self.assertEqual(str(messages[0]), 'Password reset link has been sent to your WhatsApp number.')

        # Check if WhatsApp message sending logic is called (assuming it exists)
        # If using mock for WhatsApp, add an assertion to check if it was called
        # e.g., mock_whatsapp_message.assert_called_once_with('+1234567890', expected_message)

    def test_forgot_password_non_existent_phone(self):
        """Test when a valid phone number is provided but user doesn't exist."""
        response = self.client.post(reverse('forgot_password'), {'identifier': '+9999999999'})
        
        # Ensure the error message is displayed
        self.assertRedirects(response, reverse('forgot_password'))
        messages = list(response.wsgi_request._messages)
        self.assertEqual(str(messages[0]), 'Account does not exist.')

    def test_forgot_password_invalid_identifier(self):
        """Test when an invalid identifier is provided (neither phone nor email)."""
        response = self.client.post(reverse('forgot_password'), {'identifier': 'invalid-identifier'})
        
        # Ensure the error message is displayed
        self.assertRedirects(response, reverse('forgot_password'))
        messages = list(response.wsgi_request._messages)
        self.assertEqual(str(messages[0]), 'Please enter a valid email address or phone number.')

    def test_valid_reset_password(self):
        """Test a valid password reset process."""
        session = self.client.session
        session['uid'] = self.user.pk
        session.save()

        response = self.client.post(reverse('reset_password'), {
            'password': 'newpassword123',
            'confirm_password': 'newpassword123',
        })
        self.assertRedirects(response, reverse('login'))
        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password('newpassword123'))

    def test_invalid_token(self):
        """Test resetting the password with an invalid token."""
        invalid_token = 'invalid-token'
        response = self.client.get(reverse('reset_password_validate', kwargs={
        'uidb64': self.uidb64,
        'token': invalid_token,
        }), follow=True)
        self.assertEqual(response.status_code, 200)
        
        self.assertContains(response, 'This link has expired or is invalid.')

    def test_password_mismatch(self):
        """Test when passwords do not match."""
        session = self.client.session
        session['uid'] = self.user.pk
        session.save()

        response = self.client.post(reverse('reset_password'), {
            'password': 'newpassword123',
            'confirm_password': 'differentpassword123',
        })
        self.assertRedirects(response, reverse('reset_password'))
        messages = list(response.wsgi_request._messages)
        self.assertEqual(str(messages[0]), "Passwords do not match.")
        
    
    def test_customer_contact_us_url(self):
        """Test customer contact us URL and view."""
        self.client.login(username='testuser@example.com', password='password123')
        response = self.client.get(reverse('c_contact_us'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'accounts/c_contactUs.html')

        response = self.client.post(reverse('c_contact_us'), {
            'name': 'Customer',
            'message': 'Need assistance with order'
        })

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'accounts/c_contactUs.html')

        self.assertTrue(response.context['form_submitted'])

        messages = list(response.wsgi_request._messages)
        self.assertEqual(str(messages[0]), 'Thank you for reaching out! Your message has been sent successfully.')


    def test_restaurant_contact_us_url(self):
        """Test customer contact us URL and view."""
        self.client.login(username='restaurantnew3@example.com', password='password123')
        response = self.client.get(reverse('r_contact_us'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'accounts/r_contactUs.html')

        response = self.client.post(reverse('r_contact_us'), {
            'name': 'Restaurant',
            'message': 'Need assistance with restaurant on boarding.'
        })

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'accounts/r_contactUs.html')

        self.assertTrue(response.context['form_submitted'])

        messages = list(response.wsgi_request._messages)
        self.assertEqual(str(messages[0]), 'Thank you for reaching out! Your message has been sent successfully.')
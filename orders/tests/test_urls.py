from django.test import TestCase
from django.urls import reverse
from accounts.models import User

class OrderURLsTest(TestCase):

    def setUp(self):
        # Create and log in a test user, assuming login is required for the views
        self.user = User.objects.create_user(
            username='testuser@gmail.com', 
            password='testpass',
            first_name='Test', 
            last_name='User'
        )
        self.client.login(username='testuser@gmail.com', password='testpass')
        
    def test_place_order_url_resolves(self):
        """Test that the place_order URL resolves correctly and returns a 200 status code."""
        response = self.client.get(reverse('place_order'))
        if response.status_code == 302:
            # If redirected, follow the redirect and check for successful response
            response = self.client.get(response.url)
        self.assertEqual(response.status_code, 200)

    def test_payments_url_resolves(self):
        """Test that the payments URL resolves correctly and returns a 200 status code."""
        response = self.client.get(reverse('payments'))
        self.assertEqual(response.status_code, 200)

    def test_order_complete_url_resolves(self):
        """Test that the order_complete URL resolves correctly and returns a 200 status code."""
        response = self.client.get(reverse('order_complete'))
        if response.status_code == 302:
            # If redirected, follow the redirect and check for successful response
            response = self.client.get(response.url)
        self.assertEqual(response.status_code, 200)

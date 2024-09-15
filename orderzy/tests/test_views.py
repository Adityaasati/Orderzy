from django.test import TestCase, RequestFactory
from django.contrib.gis.geos import Point
from restaurant.models import Restaurant
from accounts.models import User, UserProfile
from django.urls import reverse
from orderzy.views import home, get_or_set_current_location
from restaurant.models import Restaurant,FoodHub
from django.contrib.auth.models import AnonymousUser

class HomeViewTest(TestCase):
    def setUp(self):
        self.factory = RequestFactory()

        # Create a user and restaurant with geolocation
        self.user = User.objects.create_user(
            first_name='John',
            last_name='Doe',
            username='john@example.com',
            password='testpass123'
        )
        self.location = Point(77.594566, 12.9715987)  # Bangalore coordinates
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
            is_approved=True,
            food_hub=self.food_hub,
        )
        self.anonymous_user = AnonymousUser()

    def test_home_view_with_location(self):
        # Test home view when location is in session
        request = self.factory.get('/')
        request.session = {'lat': '12.9715987', 'lng': '77.594566'}
        request.user = self.anonymous_user  # Set as anonymous user

        response = home(request)

        self.assertEqual(response.status_code, 200)
        self.assertIn('restaurants', response.content.decode())
        # self.assertEqual(len(response.context['restaurants']), 1)  # Since we added only one restaurant

    def test_home_view_without_location(self):
        # Test home view when location is not in session or GET params
        request = self.factory.get('/')
        request.session = {}
        request.user = self.anonymous_user  # Set as anonymous user

        response = home(request)

        self.assertEqual(response.status_code, 200)
        # self.assertIn('restaurants', response.context)  # Since we added only one approved restaurant

    def test_home_view_with_get_params_location(self):
        # Test home view when lat/lng are passed as GET params
        request = self.factory.get('/?lat=12.9715987&lng=77.594566')
        request.session = {}
        request.user = self.anonymous_user
        response = home(request)

        self.assertEqual(response.status_code, 200)
        self.assertIn('restaurants', response.content.decode())
        # self.assertEqual(len(response.context['restaurants']), 1)
        self.assertIn('lat', request.session)
        self.assertIn('lng', request.session)

    def test_home_view_with_invalid_location(self):
        # Test home view with an invalid location (e.g., missing lat/lng)
        request = self.factory.get('/')
        request.session = {'lat': 'invalid', 'lng': 'invalid'}
        request.user = AnonymousUser()
        response = home(request)
        
        self.assertEqual(response.status_code, 200)
        self.assertIn('restaurants', response.content.decode())
        # self.assertEqual(len(response.context['restaurants']), 1)  # Should default to non-location-based filtering



class LocationHelperTest(TestCase):
    def setUp(self):
        self.factory = RequestFactory()

    def test_get_location_from_session(self):
        # Test when lat/lng are in session
        request = self.factory.get('/')
        request.session = {'lat': '12.9715987', 'lng': '77.594566'}
        lng, lat = get_or_set_current_location(request)
        self.assertEqual(lat, 12.9715987)
        self.assertEqual(lng, 77.594566)

    def test_get_location_from_get_params(self):
        # Test when lat/lng are in GET params
        request = self.factory.get('/?lat=12.9715987&lng=77.594566')
        request.session = {}
        lng, lat = get_or_set_current_location(request)
        self.assertEqual(lat, 12.9715987)
        self.assertEqual(lng, 77.594566)
        self.assertIn('lat', request.session)
        self.assertIn('lng', request.session)

    def test_get_location_returns_none(self):
        # Test when lat/lng are not in session or GET params
        request = self.factory.get('/')
        request.session = {}
        location = get_or_set_current_location(request)
        self.assertIsNone(location)

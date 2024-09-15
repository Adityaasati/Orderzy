from django.test import TestCase
from django.contrib.sites.models import Site
from accounts.models import User, UserProfile
from restaurant.models import FoodHub, Restaurant, OpeningHour, SeatingPlan
from django.contrib.gis.geos import Point
from datetime import datetime
from unittest.mock import patch


class FoodHubModelTest(TestCase):

    def setUp(self):
        self.food_hub = FoodHub.objects.create(
            foodhub_name="Test Food Hub",
            latitude="12.9716",
            longitude="77.5946"
        )

    def test_foodhub_creation(self):
        """Test if the FoodHub is created properly and the location is set"""
        self.assertEqual(self.food_hub.foodhub_name, "Test Food Hub")
        expected_point = Point(float(77.5946), float(12.9716))  # longitude, latitude
        self.assertAlmostEqual(self.food_hub.location.x, expected_point.x, places=5)
        self.assertAlmostEqual(self.food_hub.location.y, expected_point.y, places=5)  # longitude, latitude

    def test_foodhub_str(self):
        """Test the string representation of the FoodHub model"""
        self.assertEqual(str(self.food_hub), "Test Food Hub")


class RestaurantModelTest(TestCase):

    @patch('restaurant.models.send_notification')
    def setUp(self, mock_send_notification):
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
        self.opening_hour = OpeningHour.objects.create(
            restaurant=self.restaurant,
            day=datetime.today().isoweekday(),  # current day of the week
            from_hour="09:00 AM",
            to_hour="05:00 PM",
            is_closed=False,
        )
        

    def test_restaurant_creation(self):
        """Test if the Restaurant is created properly"""
        self.assertEqual(self.restaurant.restaurant_name, "Test Restaurant")
        self.assertEqual(self.restaurant.food_hub, self.food_hub)
        self.assertFalse(self.restaurant.is_approved)

    def test_restaurant_slug_creation(self):
        """Test if the slug is created properly when the Restaurant is saved"""
        self.restaurant.save()
        expected_slug = f"test-restaurant-{self.user.id}"
        self.assertEqual(self.restaurant.restaurant_slug, expected_slug)

    @patch('restaurant.models.send_notification')
    def test_restaurant_approval_notification(self, mock_send_notification):
        """Test if the approval notification is sent when a restaurant is approved"""
        self.restaurant.is_approved = True
        self.restaurant.save()

        self.assertTrue(mock_send_notification.called)
        mock_send_notification.assert_called_with(
            "Congrats, Your Restaurant has been approved",
            'accounts/emails/admin_approval_email.html',
            {
                'user': self.user,
                'is_approved': True,
                'to_email': self.user.email,
            }
        )

    @patch('restaurant.models.generate_qr')
    def test_qr_code_generation_on_save(self, mock_generate_qr):
        """Test if the QR code is generated after saving the Restaurant"""
        self.restaurant.save()
        mock_generate_qr.assert_called_with(self.restaurant.menu_url, self.restaurant.qr_code_path)

    @patch('restaurant.models.datetime', wraps=datetime) 
    def test_is_open(self, mock_datetime):
        """Test if the restaurant is open during its working hours"""
    
        mock_datetime.now.return_value = datetime(2024, 9, 10, 12, 0, 0)  # Return full datetime object with 12:00 PM
    
        mock_datetime.today.return_value = datetime(2024, 9, 10)  # Assume this is the current date
    
        self.assertTrue(self.restaurant.is_open(), "Restaurant should be open at 12:00 PM")
    
    
        mock_datetime.now.return_value = datetime(2024, 9, 10, 20, 0, 0)  # Return full datetime object with 08:00 PM
    
    
        self.assertFalse(self.restaurant.is_open(), "Restaurant should be closed at 08:00 PM")
         
class OpeningHourModelTest(TestCase):

    def setUp(self):
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
        self.opening_hour = OpeningHour.objects.create(
            restaurant=self.restaurant,
            day=1,  
            from_hour="09:00 AM",
            to_hour="05:00 PM",
            is_closed=False,
        )

    def test_opening_hour_creation(self):
        """Test if the OpeningHour is created properly"""
        self.assertEqual(self.opening_hour.day, 1)

    def test_opening_hour_str(self):
        """Test the string representation of the OpeningHour model"""
        self.assertEqual(str(self.opening_hour), "Monday")


class SeatingPlanModelTest(TestCase):

    def setUp(self):
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
        
        self.seating_plan = SeatingPlan.objects.create(
            restaurant=self.restaurant,
            seating_plan_available=True,
            tables_for_two=5,
            tables_for_four=3,
            tables_for_six=2,
        )

    def test_seating_plan_creation(self):
        """Test if the SeatingPlan is created properly"""
        self.assertEqual(self.seating_plan.restaurant, self.restaurant)
        self.assertTrue(self.seating_plan.seating_plan_available)
        self.assertEqual(self.seating_plan.tables_for_two, 5)
        self.assertEqual(self.seating_plan.tables_for_four, 3)
        self.assertEqual(self.seating_plan.tables_for_six, 2)

    def test_seating_plan_str(self):
        """Test the string representation of the SeatingPlan model"""
        self.assertEqual(str(self.seating_plan), "Seating Plan for Test Restaurant")

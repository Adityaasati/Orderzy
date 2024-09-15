
from django.test import TestCase
from restaurant.forms import *


class RestaurantFormTest(TestCase):

    def test_restaurant_form_valid_data(self):
        """Test if the restaurant form is valid with proper data"""
        form = RestaurantForm(data={
            'restaurant_name': 'Test Restaurant',
        })
        self.assertTrue(form.is_valid())
    
    def test_restaurant_form_no_data(self):
        """Test if the restaurant form is invalid without data"""
        form = RestaurantForm(data={})
        self.assertFalse(form.is_valid())
        self.assertEqual(len(form.errors), 1)  



class OpeningHourFormTest(TestCase):

    def test_opening_hour_form_invalid_data(self):
        """Test if the opening hour form is invalid with missing fields"""
        form = OpeningHourForm(data={
            'day': '',  
            'from_hour': '',
            'to_hour': '',
            'is_closed': False  
        })
        self.assertFalse(form.is_valid())
        print(form.errors,"form.errors")
        self.assertEqual(len(form.errors), 3)  # Expecting 3 errors: day, from_hour, and to_hour

    def test_opening_hour_form_closed(self):
        """Test that from_hour and to_hour are not required when is_closed is True"""
        form = OpeningHourForm(data={
            'day': 1,  # Monday
            'from_hour': '',
            'to_hour': '',
            'is_closed': True  # When the restaurant is closed, from_hour and to_hour should be optional
        })
        self.assertTrue(form.is_valid())

from django.test import TestCase
from orders.forms import OrderForm
from orders.models import Order

class OrderFormTest(TestCase):

    def setUp(self):
        self.valid_data = {
            'first_name': 'John',
            'last_name': 'Doe',
            'phone': '1234567890',
            'email': 'john@example.com',
            'pre_order_time': 30.0,
            'num_of_people': None
        }

    def test_order_form_valid(self):
        """Test form with valid data"""
        form = OrderForm(data=self.valid_data)
        self.assertTrue(form.is_valid())

    def test_order_form_missing_optional_fields(self):
        """Test form when optional fields are missing (pre_order_time, email)"""
        form_data = {
            'first_name': 'Jane',
            'last_name': 'Doe',
            'phone': '1234567890',
        }
        form = OrderForm(data=form_data)
        self.assertTrue(form.is_valid())
        self.assertEqual(form.cleaned_data['pre_order_time'], 0)  # pre_order_time should default to 0
        self.assertEqual(form.cleaned_data['email'], '')  # email should default to empty
        self.assertIsNone(form.cleaned_data['num_of_people'])   # Check default value for email
        

    def test_order_form_with_seating_plan(self):
        """Test form with restaurant and seating plan"""
        form_data = self.valid_data.copy()
        form_data.pop('num_of_people')  # Remove num_of_people to test required field
        form = OrderForm(data=form_data, restaurant=True, has_seating_plan=True)
        self.assertFalse(form.is_valid())  # Should be invalid because num_of_people is required
        self.assertIn('num_of_people', form.errors)

    def test_order_form_without_seating_plan(self):
        """Test form with restaurant but no seating plan"""
        form_data = self.valid_data.copy()
        form = OrderForm(data=form_data, restaurant=True, has_seating_plan=False)
        self.assertTrue(form.is_valid())
        self.assertIsNone(form.cleaned_data['num_of_people'])  # num_of_people should remain None

    def test_order_form_without_restaurant(self):
        """Test form without restaurant (num_of_people not required)"""
        form_data = self.valid_data.copy()
        form_data.pop('num_of_people')  # Remove num_of_people to test not required
        form = OrderForm(data=form_data)
        self.assertTrue(form.is_valid())
        self.assertIsNone(form.cleaned_data['num_of_people'])  # num_of_people should remain None

    def test_invalid_email(self):
        """Test form with invalid email"""
        form_data = self.valid_data.copy()
        form_data['email'] = 'invalid_email'
        form = OrderForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('email', form.errors)

    def test_pre_order_time_is_float(self):
        """Test that pre_order_time accepts only float values"""
        form_data = self.valid_data.copy()
        form_data['pre_order_time'] = 'not_a_float'
        form = OrderForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('pre_order_time', form.errors)


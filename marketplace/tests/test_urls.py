from django.test import SimpleTestCase
from django.urls import reverse, resolve
from marketplace import views

class TestUrls(SimpleTestCase):

    ### Test `marketplace` URL ###
    def test_marketplace_url_is_resolved(self):
        url = reverse('marketplace')
        self.assertEqual(resolve(url).func, views.marketplace)

    ### Test `restaurant_detail` URL ###
    def test_restaurant_detail_url_is_resolved(self):
        url = reverse('restaurant_detail', args=['test-restaurant'])
        self.assertEqual(resolve(url).func, views.restaurant_detail)

    ### Test `add_to_cart` URL ###
    def test_add_to_cart_url_is_resolved(self):
        url = reverse('add_to_cart', args=[1])  # Test with food_id=1
        self.assertEqual(resolve(url).func, views.add_to_cart)

    ### Test `decrease_cart` URL ###
    def test_decrease_cart_url_is_resolved(self):
        url = reverse('decrease_cart', args=[1])  # Test with food_id=1
        self.assertEqual(resolve(url).func, views.decrease_cart)

    ### Test `delete_cart` URL ###
    def test_delete_cart_url_is_resolved(self):
        url = reverse('delete_cart', args=[1])  # Test with cart_id=1
        self.assertEqual(resolve(url).func, views.delete_cart)

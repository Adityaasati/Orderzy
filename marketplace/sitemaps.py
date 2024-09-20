from django.contrib.sitemaps import Sitemap
from django.urls import reverse
from restaurant.models import Restaurant

class MarketplaceSitemap(Sitemap):
    changefreq = "daily"
    priority = 0.9

    def items(self):
        return ['marketplace', 'checkout', 'cart']

    def location(self, item):
        return reverse(item)

    def changefreq(self, item):
        if item == 'marketplace':
            return 'always'  # Restaurant listings are updated frequently
        if item == 'checkout':
            return 'hourly'  # Checkout is a transactional page
        return 'weekly'

    def priority(self, item):
        if item == 'marketplace':
            return 1.0  # Restaurant listings are critical to the app
        return 0.8

class RestaurantSitemap(Sitemap):
    changefreq = "daily"
    priority = 0.8

    def items(self):
        return Restaurant.objects.filter(is_approved=True, user__is_active=True)

    def location(self, obj):
        return reverse('restaurant_detail', args=[obj.restaurant_slug])

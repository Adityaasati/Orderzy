from django.contrib.sitemaps import Sitemap
from django.urls import reverse

class OrdersSitemap(Sitemap):
    changefreq = "daily"
    priority = 0.8

    def items(self):
        return ['order_complete']

    def location(self, item):
        return reverse(item)

    def changefreq(self, item):
        if item == 'order_complete':
            return 'daily'  # Orders get completed frequently
        return 'weekly'

    def priority(self, item):
        if item == 'order_complete':
            return 1.0  # Important as this is an order confirmation page
        return 0.8

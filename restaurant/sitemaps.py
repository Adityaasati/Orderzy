from django.contrib.sitemaps import Sitemap
from django.urls import reverse

class RestaurantSitemap(Sitemap):
    changefreq = "weekly"
    priority = 0.8

    def items(self):
        return ['rprofile', 'menu_builder', 'order_detail', 'pending_orders']

    def location(self, item):
        return reverse(item)

    def changefreq(self, item):
        if item in ['order_detail', 'pending_orders']:
            return 'always'  # Orders change daily
        return 'weekly'  # Restaurant profile and menu change less frequently

    def priority(self, item):
        if item == 'rprofile':
            return 0.9  # Restaurant profile is important but not critical for SEO
        return 0.8  # Other views are important but not as high priority

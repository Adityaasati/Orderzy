from django.contrib.sitemaps import Sitemap
from django.urls import reverse

class CustomerSitemap(Sitemap):
    changefreq = "weekly"
    priority = 0.8

    def items(self):
        return [
            'cprofile',
            'customer_my_orders',
        ]

    def location(self, item):
        return reverse(item)

    def changefreq(self, item):
        if item == 'customer_my_orders':
            return 'always'  
        return 'weekly'

    def priority(self, item):
        if item == 'cprofile':
            return 0.7  
        return 0.8

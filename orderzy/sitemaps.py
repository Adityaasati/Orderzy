from django.contrib.sitemaps import Sitemap
from django.urls import reverse

class HomeSitemap(Sitemap):
    changefreq = "daily"
    priority = 1.0

    def items(self):
        return ['home', 'base']

    def location(self, item):
        return reverse(item)

    def changefreq(self, item):
        if item == 'home':
            return 'always'  # The homepage often contains dynamic restaurant listings
        return 'weekly'  # The base page may change less frequently

    def priority(self, item):
        if item == 'home':
            return 1.0  # The homepage is critical for user navigation
        return 0.6  # The base page is more structural

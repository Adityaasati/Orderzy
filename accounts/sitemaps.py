from django.contrib.sitemaps import Sitemap
from django.urls import reverse

class AccountsSitemap(Sitemap):
    changefreq = "weekly"
    priority = 0.8
    
    def items(self):
        return [
            'registerUser',
            'registerRestaurant',
            'login',
            'forgot_password',
            'reset_password',
            'newsletter_signup'
        ]
    
    def location(self, item):
        return reverse(item)

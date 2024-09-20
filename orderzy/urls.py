"""
URL configuration for orderzy project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from . import views
from django.conf import settings
from django.conf.urls.static import static
from marketplace import views as MarketplaceViews
from django.contrib.sitemaps.views import sitemap
from .sitemaps import HomeSitemap
from marketplace.sitemaps import MarketplaceSitemap, RestaurantSitemap
from customers.sitemaps import CustomerSitemap
from accounts.sitemaps import AccountsSitemap
from orders.sitemaps import OrdersSitemap
from django.views.generic import TemplateView

sitemaps = {
    'home': HomeSitemap,
    'marketplace': MarketplaceSitemap,
    'restaurant': RestaurantSitemap,
    'customers': CustomerSitemap,
    'accounts': AccountsSitemap,
    'orders': OrdersSitemap,
}
urlpatterns = [
    path('sitemap.xml', sitemap, {'sitemaps': sitemaps}, name='django.contrib.sitemaps.views.sitemap'),
    path('robots.txt', TemplateView.as_view(template_name="robots.txt", content_type="text/plain")),
    path("admin/", admin.site.urls),
    path('', views.home, name = 'home'),
    path('base/', views.base, name = 'base'),
    
    path('', include('accounts.urls')),
    path('marketplace/', include('marketplace.urls')),
    #CART
    path('cart/', MarketplaceViews.cart, name='cart'),
    
    #SEARCH PATH
    path('search/', MarketplaceViews.search, name='search'),
    
    path('checkout/', MarketplaceViews.checkout, name='checkout'),
    
    
    path('orders/', include('orders.urls')),
    

    
    
    
] + static(settings.MEDIA_URL, document_root = settings.MEDIA_ROOT)

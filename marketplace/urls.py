from django.urls import path
from . import views
from django.contrib.sitemaps.views import sitemap



urlpatterns =[
    path('',views.marketplace, name='marketplace'),
    path('<slug:restaurant_slug>/', views.restaurant_detail, name='restaurant_detail'),
    path('add_to_cart/<int:food_id>/', views.add_to_cart, name='add_to_cart'),
    path('decrease_cart/<int:food_id>/', views.decrease_cart, name='decrease_cart'),
    path('delete_cart/<int:cart_id>', views.delete_cart, name="delete_cart"),
    
    
]
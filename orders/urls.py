from django.urls import path
from . import views
from django.contrib.sitemaps.views import sitemap




urlpatterns = [
    path('place-order/', views.place_order, name = 'place_order'),
    path('create_order_api/', views.create_order_api, name='create_order_api'),
    path('payment-webhook/', views.payment_webhook, name='payment_webhook'),
    path('order_complete/', views.order_complete, name='order_complete'),
    
]
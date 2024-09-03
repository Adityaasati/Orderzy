from django.urls import path
from accounts import views as AccountViews
from . import views


urlpatterns = [
    path('',AccountViews.custDashboard, name='customer'),
    path('profile/',views.cprofile, name='cprofile'),
    path('my_orders/', views.my_orders, name = 'customer_my_orders'),
    path('order_detail/<int:order_number>/', views.order_detail, name = 'order_detail'),
    path('order_cancel/<int:order_number>/', views.order_cancel, name = 'order_cancel'),
    path('pre_order_time_change/<int:order_number>/', views.pre_order_time_change, name = 'pre_order_time_change'),
    
    
    
]
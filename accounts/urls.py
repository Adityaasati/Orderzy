from django.urls import path,include
from . import views

urlpatterns = [
    # path('myAccount/',views.myAccount, name='account_url'),
    path('registerUser/', views.registerUser, name = 'registerUser'),
    path('registerRestaurant/', views.registerRestaurant, name = 'registerRestaurant'),
    path('login/', views.login, name = 'login'),
    path('logout/', views.logout, name = 'logout'),
    path('myAccount/', views.myAccount, name = 'myAccount'),
    path('custDashboard/', views.custDashboard, name = 'custDashboard'),
    path('restaurantDashboard/', views.restaurantDashboard, name = 'restaurantDashboard'),
    path('activate/<uidb64>/<token>/', views.activate, name="activate"),
    path('forgot_password/', views.forgot_password, name='forgot_password'),
    path('reset_password_validate/<uidb64>/<token>/', views.reset_password_validate, name='reset_password_validate'),
    path('reset_password/', views.reset_password, name='reset_password'),
    path('restaurant/', include('restaurant.urls')),
    path('customer/', include('customers.urls')),
    path('restaurant-contact-us/', views.r_contact_us, name='r_contact_us'),
    path('customer-contact-us/', views.c_contact_us, name='c_contact_us'),
    path('newsletter-signup/', views.newsletter_signup, name='newsletter_signup'),


]


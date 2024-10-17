from django.urls import path
from . import views
from accounts import views as AccountViews
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.sitemaps.views import sitemap
from .sitemaps import RestaurantSitemap

sitemaps = {
    'restaurant': RestaurantSitemap,
}

urlpatterns = [
    path('sitemap.xml', sitemap, {'sitemaps': sitemaps}, name='django.contrib.sitemaps.views.sitemap'),
    path('',AccountViews.restaurantDashboard, name='restaurant'),
    path('profile/', views.rprofile, name = 'rprofile'),
    path('menu-builder/', views.menu_builder, name='menu_builder'),
    path('menu-builder/category/<int:pk>/', views.fooditems_by_category, name='fooditems_by_category'),
    
    
    
    # CRUD
    
    path('menu-builder/category/add/', views.add_category, name='add_category'),
    path('menu-builder/category/edit/<int:pk>', views.edit_category, name='edit_category'),
    path('menu-builder/category/delete/<int:pk>', views.delete_category, name='delete_category'),
    
    
    # Fooditem CRUD
    path('menu-builder/food/add/', views.add_food, name='add_food'),
    path('menu-builder/food/edit/<int:pk>/', views.edit_food, name='edit_food'),
    path('menu-builder/food/delete/<int:pk>', views.delete_food, name='delete_food'),
    
    #  Opening Hours CRUD 

    path('opening-hours/', views.opening_hours, name='opening_hours'),
    path('opening-hours/add/', views.add_opening_hours, name='add_opening_hours'),
    path('opening-hours/remove/<int:pk>/', views.remove_opening_hours, name='remove_opening_hours'),
    
    path('order_detail/<int:order_number>',views.order_detail, name="restaurant_order_detail"),
    path('my_orders/', views.my_orders, name = 'restaurant_my_orders'),
    path('pending_orders/', views.pending_orders, name = 'restaurant_pending_orders'),
    path('accept_po/<int:id>/', views.accept_po, name = 'accept_po'),
    path('ready_po/<int:id>/', views.ready_po, name = 'ready_po'),
    path('completed_po/<int:id>/', views.completed_po, name = 'completed_po'),
    path('delete_po/<int:id>/', views.delete_po, name='delete_po'),
    path('seating-plan/', views.seating_plan_view, name='seating_plan'),
    

    ]+ static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)



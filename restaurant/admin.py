from django.contrib import admin
from restaurant.models import Restaurant, OpeningHour, SeatingPlan ,FoodHub


class FoodHubAdmin(admin.ModelAdmin):
    list_display = ['foodhub_name', 'location']
    
class RestaurantAdmin(admin.ModelAdmin):
    list_display = ('user','restaurant_name', 'is_approved', 'created_at','food_hub' )
    list_display_links = ('user','restaurant_name')
    list_editable = ('is_approved',)
    list_filter = ['food_hub']


    
class OpeningHourAdmin(admin.ModelAdmin):
    list_display = ('restaurant','day','from_hour','to_hour')
    


class SeatingPlanAdmin(admin.ModelAdmin):
    list_display = ['restaurant', 'seating_plan_available', 'tables_for_two', 'tables_for_four', 'tables_for_six']



admin.site.register(FoodHub,FoodHubAdmin)
admin.site.register(SeatingPlan, SeatingPlanAdmin)
admin.site.register(Restaurant,RestaurantAdmin)
admin.site.register(OpeningHour,OpeningHourAdmin)

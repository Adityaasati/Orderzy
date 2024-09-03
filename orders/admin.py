from django.contrib import admin
from .models import Payment, Order,OrderedFood, PendingOrder

class OrderedFoodInline(admin.TabularInline):
    model = OrderedFood
    readonly_fields = ('order','payment','user','fooditem','quantity','price','amount')
    extra = 0
    
    
class OrderAdmin(admin.ModelAdmin):
    list_display = ['order_number','name', 'phone','email','total','num_of_people','payment_method','status','order_placed_to','is_ordered','get_total_by_restaurant']
    inlines = [OrderedFoodInline]
  


class PendingOrderAdmin(admin.ModelAdmin):
    list_display = ['po_id','po_order_number','po_restaurant_order','po_restaurant_id','po_num_of_people','po_status','po_order_type','po_name','po_total','po_pre_order_time','order_placed_to','preparing_restaurant_order_number','get_restaurant_order_number','po_ordered_food_details','po_is_ordered']


admin.site.register(PendingOrder,PendingOrderAdmin)
admin.site.register(Payment)
admin.site.register(Order,OrderAdmin)
admin.site.register(OrderedFood)

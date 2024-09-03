from django.contrib import admin
from .models import Cart,Service_Charge

class CartAdmin(admin.ModelAdmin):
    list_display = ('user','fooditem','quantity','updated_at')


class Service_ChargeAdmin(admin.ModelAdmin):
    list_display = ('service_charge_type','service_charge_percentage', 'is_active')

admin.site.register(Cart,CartAdmin)
admin.site.register(Service_Charge,Service_ChargeAdmin)
from django.db import models
from accounts.models import User
from menu.models import FoodItem


class Cart(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    fooditem = models.ForeignKey(FoodItem, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    
    def __unicode__(self):
        return self.user
    
    
class Service_Charge(models.Model):
    service_charge_type = models.CharField(max_length=20, unique=True)
    service_charge_percentage = models.DecimalField(decimal_places=2, max_digits=4, verbose_name  = 'Service_Charge_percentage(%)')
    is_active = models.BooleanField(default=True)
    
    
    class Meta:
        verbose_name_plural = 'Service_charge'
    
    def __str__(self):
        return self.service_charge_type
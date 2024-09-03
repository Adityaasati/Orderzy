from django import forms 
from .models import Restaurant, OpeningHour, SeatingPlan
from accounts.validators import allow_only_images_validator


class RestaurantForm(forms.ModelForm):
    
    class Meta:
        model = Restaurant
        fields = ['restaurant_name']
        
class OpeningHourForm(forms.ModelForm):
    class Meta:
        model = OpeningHour
        fields = ['day','from_hour','to_hour','is_closed']
        
        


class SeatingPlanForm(forms.ModelForm):
    class Meta:
        model = SeatingPlan
        fields = ['seating_plan_available', 'tables_for_two', 'tables_for_four', 'tables_for_six']

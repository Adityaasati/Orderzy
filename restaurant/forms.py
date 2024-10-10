from django import forms 
from datetime import time
from .models import Restaurant, OpeningHour, SeatingPlan
from accounts.validators import allow_only_images_validator


class RestaurantForm(forms.ModelForm):
    
    class Meta:
        model = Restaurant
        fields = ['restaurant_name']
        


HOURS_OF_DAY_24 = [(time(h, m), time(h, m).strftime('%I:%M %p')) for h in range(0, 24) for m in (0, 30)]

class OpeningHourForm(forms.ModelForm):
    from_hour = forms.ChoiceField(choices=HOURS_OF_DAY_24, required=False)
    to_hour = forms.ChoiceField(choices=HOURS_OF_DAY_24, required=False)

    class Meta:
        model = OpeningHour
        fields = ['day', 'from_hour', 'to_hour', 'is_closed']
        
    def clean(self):
        cleaned_data = super().clean()
        is_closed = cleaned_data.get('is_closed')
        from_hour = cleaned_data.get('from_hour')
        to_hour = cleaned_data.get('to_hour')

        if not is_closed:
            if not from_hour:
                self.add_error('from_hour', 'This field is required when the restaurant is open.')
            if not to_hour:
                self.add_error('to_hour', 'This field is required when the restaurant is open.')

        return cleaned_data

class SeatingPlanForm(forms.ModelForm):
    class Meta:
        model = SeatingPlan
        fields = ['seating_plan_available', 'tables_for_two', 'tables_for_four', 'tables_for_six']

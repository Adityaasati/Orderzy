
from django import forms
from .models import Order

class OrderForm(forms.ModelForm):
    pre_order_time = forms.FloatField(required=False, initial=0)
    email = forms.EmailField(required=False)
    
    def __init__(self, *args, **kwargs):
        restaurant = kwargs.pop('restaurant', None)  # Get restaurant from kwargs
        has_seating_plan = kwargs.pop('has_seating_plan', False)  # Determine if there's a seating plan
        super(OrderForm, self).__init__(*args, **kwargs)
        
        if restaurant and has_seating_plan:
            self.fields['num_of_people'].required = True
            self.fields['num_of_people'].initial = None 
            
        else:
            self.fields['num_of_people'].required = False
            self.fields['num_of_people'].initial = 0
    
    class Meta:
        model = Order
        fields = ['first_name', 'last_name', 'phone', 'email', 'pre_order_time', 'num_of_people']

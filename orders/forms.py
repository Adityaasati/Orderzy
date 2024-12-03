
from django import forms
from .models import Order

class OrderForm(forms.ModelForm):
    pre_order_time = forms.FloatField(required=False, initial=0)
    email = forms.EmailField(required=False)
    num_of_people = forms.IntegerField(required=False, initial=None)
    seat_number = forms.CharField(required=False, initial=None)
    
    
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
            
    def clean_pre_order_time(self):
        """Ensure pre_order_time defaults to 0 if not provided."""
        pre_order_time = self.cleaned_data.get('pre_order_time', None)
        if pre_order_time is None:
            return 0
        return pre_order_time

    def clean_num_of_people(self):
        """Ensure num_of_people remains None if not set."""
        num_of_people = self.cleaned_data.get('num_of_people', None)
        if num_of_people == '':
            return None
        return num_of_people
    class Meta:
        model = Order
        fields = ['first_name', 'last_name', 'phone', 'email', 'pre_order_time', 'num_of_people']

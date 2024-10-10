from django import forms
from .models import *
from accounts.validators import allow_only_images_validator

class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ['category_name', 'description']
        

class FoodItemForm(forms.ModelForm):
    FOOD_TYPE_CHOICES = [
        ('veg', 'Vegetarian'),
        ('non-veg', 'Non-Vegetarian'),
    ]
    food_type = forms.ChoiceField(choices=FOOD_TYPE_CHOICES, required=True, label="Food Type")
    quantity = forms.IntegerField( label="Quantity", required=False)

    image = forms.FileField(
        widget=forms.FileInput(attrs={'class': 'btn btn-info w-100'}),
        validators=[allow_only_images_validator],
        required=False  
    )
    class Meta:
        model = FoodItem
        fields = ['category','food_title', 'description','price','image','is_available','food_type', 'quantity']
from django import forms
from .models import *
from .validators import allow_only_images_validator

        
class UserForm(forms.ModelForm):
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'placeholder': 'Enter your password'
        })
    )

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'username','password']
    
    def __init__(self, *args, **kwargs):
        super(UserForm, self).__init__(*args, **kwargs)
        self.fields['username'].widget.attrs.update({
            'placeholder': 'Please enter your email or phone number'
        })
    def clean(self):
        cleaned_data = super().clean()
        username = cleaned_data.get('username')

        if not username:
            raise forms.ValidationError("Username is required.")
        
        if '@' in username:
            email = username
            if User.objects.filter(username=email).exists():
                raise forms.ValidationError("User with this Email already exists.")
        else:
            phone_number = username
            if User.objects.filter(username=phone_number).exists():
                raise forms.ValidationError("User with this Phone Number already exists.")

        return cleaned_data
    
class UserProfileForm(forms.ModelForm):
    address = forms.CharField(widget=forms.TextInput(attrs={'placeholder' : 'Start Typing...', 'required':'required'}))
    profile_picture = forms.FileField(widget = forms.FileInput(attrs={'class':'btn btn-info'}), validators=[allow_only_images_validator])
    cover_photo = forms.FileField(widget = forms.FileInput(attrs={'class':'btn btn-info'}), validators=[allow_only_images_validator])
    
    
    class Meta:
        model = UserProfile
        fields = ['profile_picture','cover_photo','address','country','state','city','pin_code','latitude','longitude']
        
        
    def __init__(self, *args, **kwargs):
        super(UserProfileForm, self).__init__(*args, **kwargs)
        for field in self.fields:
            if field =='latitude' or field == 'longitude':
                self.fields[field].widget.attrs['readonly'] = 'readonly'
                
                

class UserInfoForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['first_name','last_name','phone_number']
        
        



class LoginForm(forms.Form):
    identifier = forms.CharField(max_length=255, widget=forms.TextInput(attrs={'placeholder': 'Email or Mobile Number'}))
    password = forms.CharField(widget=forms.PasswordInput())



class ContactForm(forms.ModelForm):
    class Meta:
        model = ContactMessage
        fields = ['name', 'message']



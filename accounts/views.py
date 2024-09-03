from django.shortcuts import render
from .forms import UserForm, LoginForm, ContactForm
from django.shortcuts import redirect, render
from .models import User, UserProfile, ContactMessage
from django.contrib import messages
from restaurant.forms import RestaurantForm
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import auth
from django.shortcuts import render
from .utils import detectUser, send_verification_email
from django.core.exceptions import PermissionDenied
from django.utils.http import urlsafe_base64_decode
from django.contrib.auth.tokens import default_token_generator
from restaurant.models import Restaurant
from django.template.defaultfilters import slugify
from orders.models import Order
from django.conf import settings
import os
import datetime
import re

def check_role_restaurant(user):
    if user.role == 1:
        return True
    else:
        raise PermissionDenied

def check_role_customer(user):
    if user.role ==2:
        return True
    else:
        raise PermissionDenied


def registerUser(request):
    if request.user.is_authenticated:
        messages.warning(request, "You are already logged in")
        return redirect('custDashboard')
    elif request.method == 'POST':
        form = UserForm(request.POST)
        if form.is_valid():  
            first_name = form.cleaned_data['first_name']
            last_name = form.cleaned_data['last_name']
            username = form.cleaned_data['username']
            email = form.cleaned_data.get('email') 
            phone_number = form.cleaned_data.get('phone_number')
            password = form.cleaned_data['password']
            
            user = User.objects.create_user(
                first_name=first_name, last_name=last_name, 
                username=form.cleaned_data['username'], 
                email=email,phone_number=phone_number,
                password=password)
            user.role = User.CUSTOMER
            user.save()
            user.is_active = True
            user.save()
            messages.success(request, "Your Account has been registered successfully!")
            return redirect('login')
        else:
            print("Invalid form")
            print(form.errors)
    else:
        form = UserForm()
    context = {
        'form':form,
    }
    return render(request, 'accounts/registerUser.html', context)

def registerRestaurant(request):
    if request.user.is_authenticated:
        messages.warning(request, "You are already logged in")
        return redirect('restaurantDashboard')
    elif request.method == 'POST':
        form = UserForm(request.POST)
        r_form = RestaurantForm(request.POST, request.FILES) 
        if form.is_valid() and r_form.is_valid():
            first_name = form.cleaned_data['first_name']
            last_name = form.cleaned_data['last_name']
            username = form.cleaned_data['username']
            email = form.cleaned_data.get('email')  
            phone_number = form.cleaned_data.get('phone_number') 
            password = form.cleaned_data['password']
            user = User.objects.create_user(
                first_name=first_name, last_name=last_name, 
                username=form.cleaned_data['username'], 
                email=email, phone_number=phone_number, password=password)
            user.role = User.RESTAURANT
            user.save()
            restaurant = r_form.save(commit=False)
            restaurant.user = user
            restaurant_name = r_form.cleaned_data['restaurant_name']
            restaurant.restaurant_slug = slugify(restaurant_name)+'-'+str(user.id)
            user_profile = UserProfile.objects.get(user=user)
            restaurant.user_profile = user_profile
            restaurant.save()
            if re.match(r"[^@]+@[^@]+\.[^@]+", username):
                mail_subject = "Please activate your Account."
                email_template = 'accounts/emails/account_verification_email.html'
                send_verification_email(request, user, mail_subject, email_template)
                # send_verification_email(request, user, mail_subject, email_template)
                print(f"Sending email to {username}")
            elif re.match(r"^\+?\d{10,15}$", username):
                # Username is a phone number, send WhatsApp message
                message = "Please activate your account using the following code: 12345" 
                # send_whatsapp_message(username, message)
                print(f"Sending WhatsApp message to {username}")
            else:
                # Invalid username format
                messages.error(request, "Invalid username format.")
                return redirect('registerUser')
            messages.success(request, 'Your Account is created successfully. Please wait for the Approval.')
            return redirect('registerRestaurant')
        else:
            print(form.errors)
    else:
        
        form  = UserForm()
        r_form = RestaurantForm()
    
    context = {
        'form':form,
        'r_form': r_form,
    }
    return render(request, 'accounts/registerRestaurant.html', context)



def login(request):
    if request.user.is_authenticated:
        messages.warning(request, "You are already logged in")
        return redirect('myAccount')
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['identifier']
            password = form.cleaned_data['password']
            user = auth.authenticate(request, username=username, password=password)
            if user.is_active:
                
                if user is not None :
                
                    auth.login(request, user)
                    messages.success(request, 'You are logged in')
                    return redirect('marketplace')
                else:
                    messages.error(request, 'Invalid credentials')
            else:
                messages.error(request, 'Kindly wait until you receive approval before proceeding.')
        else: 
            print(form.errors) 
    else:
        
        form = LoginForm()
    return render(request, 'accounts/login.html', {'form': form})


def activate(request, uidb64, token):
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = User._default_manager.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

    if user is not None and default_token_generator.check_token(user, token):
        user.is_active = True
        user.save()

        if re.match(r"[^@]+@[^@]+\.[^@]+", user.username):
            messages.success(request, 'Congrats! Your account is activated.')
            return redirect('myAccount')
        else:
            messages.error(request, 'Invalid Activation Link')
            return redirect('myAccount')
            
    elif re.match(r"^\+?\d{10,15}$", user.username):
        message = "Congrats! Your account is activated."
            # send_activate_message(user.username, message)
        print(f"Sending WhatsApp activation message to {user.username}")
    else:
        messages.error(request, 'Invalid Activation Link')
        return redirect('myAccount')


def logout(request):
    auth.logout(request)
    messages.info(request, "You are Logged out!")
    return redirect('login')

@login_required(login_url='login')
def myAccount(request):
    user = request.user
    redirectUrl = detectUser(user)
    return redirect(redirectUrl)

@login_required(login_url='login')
@user_passes_test(check_role_customer)
def custDashboard(request):
    orders = Order.objects.filter(user=request.user, is_ordered=True)
    recent_orders = orders[:5]
    context = {
        'orders': orders,
        'orders_count':orders.count(),
        'recent_orders':recent_orders,
    }
    return render(request, 'accounts/custDashboard.html',context)

@login_required(login_url='login')
@user_passes_test(check_role_restaurant)
def restaurantDashboard(request):
    restaurant = Restaurant.objects.get(user=request.user)
    orders = Order.objects.filter( restaurants__in=[restaurant.id],is_ordered=True).order_by('-created_at')
    recent_orders = orders[:10]

    current_month = datetime.datetime.now().month
    current_month_orders = orders.filter(restaurants__in=[restaurant.id], created_at__month=current_month)
    current_month_revenue = 0
    for i in current_month_orders:
        current_month_revenue += i.get_total_by_restaurant()['subtotal']
    
    filename = f"{restaurant.id}_menu_qr.png"
    file_path = os.path.join(settings.STATIC_URL, 'qr_codes', filename)
    print('file_path',file_path)
    
    total_revenue = 0
    for i in orders:
        total_revenue +=i.get_total_by_restaurant()['subtotal']
    
    context = {
        'orders':orders,
        'restaurant' : restaurant,
        'orders_count':orders.count(),
        'recent_orders':recent_orders,
        'total_revenue':total_revenue,
        'current_month_revenue':current_month_revenue,
        'qr_code_path':file_path,
        
    }
    return render(request, 'accounts/restaurantDashboard.html',context)


@login_required(login_url='login')
def contact_us(request):
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            name = form.cleaned_data['name']
            message = form.cleaned_data['message']

            ContactMessage.objects.create(
                user=request.user,
                name=name,
                message=message
            )

            messages.success(request, 'Thank you for reaching out! Your message has been sent successfully.')
            return render(request, 'accounts/contactUs.html', {'form_submitted': True})

    else:
        form = ContactForm()

    return render(request, 'contactUs.html', {'form': form, 'form_submitted': False})






# def forgot_password(request):
#     if request.method == 'POST':
#         email = request.POST['email']
        
#         if User.objects.filter(email=email).exists():
#             user = User.objects.get(email__exact=email)
            
#             mail_subject = "Reset Your Password"
#             email_template = 'accounts/emails/reset_password_email.html'
#             send_verification_email(request, user,mail_subject,email_template)
#             messages.success(request,'Password reset link has been sent to your emaill')
#             return redirect('login')
#         else:
#             messages.error(request,'Account does not exist')
#             return redirect('forgot_password')
#     return render(request, 'accounts/forgot_password.html')

import re

# def forgot_password_message(phone_number, message):
#     # Logic to send a WhatsApp message
#     pass

# def forgot_password(request):
#     if request.method == 'POST':
#         identifier = request.POST['identifier']

#         # Check if the identifier is an email or phone number
#         if re.match(r"[^@]+@[^@]+\.[^@]+", identifier):
#             # Identifier is an email
#             if User.objects.filter(email=identifier).exists():
#                 user = User.objects.get(email__exact=identifier)
                
#                 mail_subject = "Reset Your Password"
#                 email_template = 'accounts/emails/reset_password_email.html'
#                 send_verification_email(request, user, mail_subject, email_template)
#                 messages.success(request, 'Password reset link has been sent to your email')
#                 return redirect('login')
#             else:
#                 messages.error(request, 'Account does not exist')
#                 return redirect('forgot_password')

#         # elif re.match(r"^\+?\d{10,15}$", identifier):
#         #     # Identifier is a phone number
#         #     if User.objects.filter(username=identifier).exists():
#         #         user = User.objects.get(username=identifier)

#         #         reset_link = request.build_absolute_uri(
#         #             reverse('reset_password_confirm', kwargs={
#         #                 'uidb64': urlsafe_base64_encode(force_bytes(user.pk)),
#         #                 'token': default_token_generator.make_token(user),
#         #             })
#         #         )
#         #         whatsapp_message = f"Reset your password by clicking the link: {reset_link}"
#         #         forgot_password_message(identifier, whatsapp_message)
#         #         messages.success(request, 'Password reset link has been sent to your WhatsApp number')
#         #         return redirect('login')
#             # else:
#             #     messages.error(request, 'Account does not exist')
#             #     return redirect('forgot_password')

#         else:
#             messages.error(request, 'Please enter a valid email address or phone number')
#             return redirect('forgot_password')

#     return render(request, 'accounts/forgot_password.html')


import re

def forgot_password(request):
    if request.method == 'POST':
        identifier = request.POST.get('identifier')  # Use get to avoid KeyError

        # Check if the identifier is an email
        if re.match(r"[^@]+@[^@]+\.[^@]+", identifier):
            if User.objects.filter(email=identifier).exists():
                user = User.objects.get(email__exact=identifier)

                mail_subject = "Reset Your Password"
                email_template = 'accounts/emails/reset_password_email.html'
                send_verification_email(request, user, mail_subject, email_template)
                messages.success(request, 'Password reset link has been sent to your email')
                return redirect('login')
            else:
                messages.error(request, 'Account does not exist')
                return redirect('forgot_password')

        # Check if the identifier is a phone number
        # elif re.match(r"^\+?\d{10,15}$", identifier):
        #     if User.objects.filter(username=identifier).exists():
        #         user = User.objects.get(username=identifier)

        #         reset_link = request.build_absolute_uri(
        #             reverse('reset_password_confirm', kwargs={
        #                 'uidb64': urlsafe_base64_encode(force_bytes(user.pk)),
        #                 'token': default_token_generator.make_token(user),
        #             })
        #         )
        #         whatsapp_message = f"Reset your password by clicking the link: {reset_link}"
        #         send_whatsapp_message(identifier, whatsapp_message)
        #         messages.success(request, 'Password reset link has been sent to your WhatsApp number')
        #         return redirect('login')
        #     else:
        #         messages.error(request, 'Account does not exist')
        #         return redirect('forgot_password')

        else:
            messages.error(request, 'Please enter a valid email address or phone number')
            return redirect('forgot_password')

    return render(request, 'accounts/forgot_password.html')



def reset_password_validate(request, uidb64, token):
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = User._default_manager.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user=None
    if user is not None and default_token_generator.check_token(user, token):
        request.session['uid'] = uid
        messages.info(request, 'Please Reset Your Password')
        return redirect('reset_password')
    else:
        messages.error(request, 'This link has been expired')
        return redirect('myAccount')

def reset_password(request):
    if request.method == 'POST':
        password = request.POST['password']
        confirm_password = request.POST['confirm_password']
        
        if password == confirm_password:
            pk = request.session.get('uid')
            user = User.objects.get(pk=pk)
            user.set_password(password)
            user.is_active = True
            user.save()
            messages.success(request, 'Password reset Successfully')
            return redirect('login')
            
        else:
            messages.error(request, "Password does not match")
            return redirect('reset_password')
        
    return render(request, 'accounts/reset_password.html')

# accounts/views.py
# from django.contrib.auth import authenticate, login as auth_login
# from django.shortcuts import render, redirect
# from django.contrib import messages
# from .forms import UserForm, LoginForm


# def login(request):
#     if request.user.is_authenticated:
#         messages.warning(request, "You are already logged in")
#         return redirect('myAccount')

#     if request.method == 'POST':
#         form = LoginForm(request.POST)
#         if form.is_valid():
#             username = form.cleaned_data['username']
#             password = form.cleaned_data['password']
#             user = authenticate(request, username=username, password=password)
#             if user is not None:
#                 auth_login(request, user)
#                 messages.success(request, 'You are logged in')
#                 return redirect('marketplace')
#             else:
#                 messages.error(request, 'Invalid Credentials')
#                 return redirect('login')
#     else:
#         form = LoginForm()

#     return render(request, 'accounts/login.html', {'form': form})

# def registerUser(request):
#     if request.user.is_authenticated:
#         messages.warning(request, "You are already logged in")
#         return redirect('custDashboard')

#     if request.method == 'POST':
#         form = UserForm(request.POST)
#         if form.is_valid():
#             first_name = form.cleaned_data['first_name']
#             last_name = form.cleaned_data['last_name']
#             username = form.cleaned_data['username']
#             email = form.cleaned_data['email']
#             phone_number = form.cleaned_data.get('phone_number', '')
#             password = form.cleaned_data['password']
#             user = User.objects.create_user(first_name=first_name, last_name=last_name, username=username, email=email, phone_number=phone_number, password=password)
#             user.role = User.CUSTOMER
#             user.save()
#             user.is_active = True
#             user.save()
#             messages.success(request, "Your Account has been registered successfully!")
#             return redirect('registerUser')
#         else:
#             messages.error(request, form.errors)
#     else:
#         form = UserForm()

#     return render(request, 'accounts/registerUser.html', {'form': form})

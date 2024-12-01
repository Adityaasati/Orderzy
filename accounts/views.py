from .forms import UserForm, LoginForm, ContactForm
from django.shortcuts import redirect, render
from .models import User, UserProfile, ContactMessage,Newsletter
from django.contrib import messages
from django.core.exceptions import ObjectDoesNotExist
from restaurant.forms import RestaurantForm
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import auth
from django.core.exceptions import ValidationError
from django.core.validators import EmailValidator, ValidationError
from django.utils.http import urlsafe_base64_encode
from django.contrib.auth.password_validation import validate_password
from .utils import detectUser, send_verification_email
from django.core.exceptions import PermissionDenied
from django.utils.http import urlsafe_base64_decode
from django.utils.encoding import force_bytes
from django.urls import reverse
from django.http import JsonResponse
from django.contrib.auth.tokens import default_token_generator
from restaurant.models import Restaurant
from django.template.defaultfilters import slugify
from orders.models import Order
from django.conf import settings
import os
import datetime
import re
import logging

logger = logging.getLogger('django')
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
            
            logger.error("Invalid form")
            logger.error(form.errors)
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
            # user.is_active = True
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
            elif re.match(r"^\+?\d{10,15}$", username):
                
                message = "Please activate your account using the following code: 12345" 
                # send_whatsapp_message(username, message)
            else:
                # Invalid username format
                messages.error(request, "Username must be a valid email or phone number.")
                return redirect('registerRestaurant')
            messages.success(request, 'Your Account is created successfully. Please wait for the Approval.')
            return redirect('login')
        else:
            return render(request, 'accounts/registerRestaurant.html', {'form': form, 'r_form': r_form})

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
            username = form.cleaned_data['identifier'].lower()
            password = form.cleaned_data['password']
            user = auth.authenticate(request, username=username, password=password)
            
            if user is not None:
                if user.is_active:
                    if user.role == user.RESTAURANT:
                        try:
                            restaurant = Restaurant.objects.get(user=user)
                            if not restaurant.is_approved:
                                messages.error(request, 'Your restaurant account is not approved yet.')
                                return redirect('login')
                        except Restaurant.DoesNotExist:
                            messages.error(request, 'Restaurant details not found.')
                            return redirect('login')
                    
                   
                    elif user.role == user.CUSTOMER:
                        # Log them in without checking for approval
                        auth.login(request, user)
                        messages.success(request, 'You are logged in as a customer')
                        return redirect('marketplace')

                    auth.login(request, user)
                    messages.success(request, 'You are logged in')
                    return redirect('marketplace')

                else:
                    messages.error(request, 'Your account is not active. Please activate it using the link sent to your email.')
            else:
                messages.error(request, 'Invalid credentials')
        else:
            logger.error(form.errors)
    else:
        form = LoginForm()
    
    return render(request, 'accounts/login.html', {'form': form})




def activate(request, uidb64, token):
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = User._default_manager.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist) as e:
        user = None

    if user is not None and default_token_generator.check_token(user, token):
        if not user.is_active:
            user.is_active = True
            user.save()


            auth.login(request, user, backend='django.contrib.auth.backends.ModelBackend')
            
            try:
                email_validator = EmailValidator()
                email_validator(user.username)  
                messages.success(request, 'Congrats! Your account is activated.')
                return redirect('myAccount')
            except ValidationError:
                if re.match(r"^\+?\d{10,15}$", user.username):
                    messages.success(request, 'Congrats! Your account is activated.')
                    return redirect('myAccount')
                else:
                    messages.error(request, 'Invalid username format.')
                    return redirect('myAccount')
        else:
            messages.info(request, 'Your account is already activated.')
            return redirect('myAccount')
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
    restaurant_slugs = []
    for order in recent_orders:
        restaurant = order.restaurants.first()  # This returns the first restaurant in the ManyToManyField
        if restaurant:
            restaurant_slugs.append(restaurant.restaurant_slug) 
            restaurant_url = restaurant.menu_url
    restaurant_slug = restaurant_slugs[0]
    context = {
        'orders': orders,
        'orders_count': orders.count(),
        'recent_orders': recent_orders,
        'restaurant_url':restaurant_url,
        'restaurant_slug':restaurant_slug
    }

    print(restaurant_slugs, "restaurant_slugs") 

    if restaurant_slugs:
        restaurant_page_url = reverse('restaurant_detail', kwargs={'restaurant_slug': restaurant_slugs[0]})
        print('restaurant_page_url:', restaurant_page_url)
    else:
        restaurant_page_url = None

    # Return the rendered template
    return render(request, 'accounts/custDashboard.html', context)

# @login_required(login_url='login')
# @user_passes_test(check_role_customer)
# def custDashboard(request):
#     orders = Order.objects.filter(user=request.user, is_ordered=True)
#     recent_orders = orders[:5]
#     restaurant_slugs = []
#     for order in recent_orders:
#         restaurants = order.order_placed_to()  # This is now a QuerySet of Restaurant objects
#         for restaurant in restaurants:
#             restaurant_slugs.append(restaurant.restaurant_slug)
#     context = {
#         'orders': orders,
#         'orders_count':orders.count(),
#         'recent_orders':recent_orders,
#         'restaurant':restaurants
#     }
#     print(restaurants,"restaurant")
#     print("restaurant.restaurant_slug",restaurants.restaurant_slug)
#     restaurant_page_url = reverse('restaurant_page', kwargs={'restaurant_id': restaurants.restaurant_slug})
#     print('restaurant_page_url',restaurant_page_url)

#     return render(request, 'accounts/custDashboard.html',context)

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
    file_path = os.path.join('qr_codes', filename)

    file_path = file_path.replace('\\', '/') 
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    
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
def r_contact_us(request):
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
            return render(request, 'accounts/r_contactUs.html', {'form_submitted': True})

    else:
        form = ContactForm()

    return render(request, 'accounts/r_contactUs.html', {'form': form, 'form_submitted': False})




def forgot_password(request):
    if request.method == 'POST':
        identifier = request.POST.get('identifier')  # Safely get identifier

        # Try to validate as an email first
        email_validator = EmailValidator()
        try:
            email_validator(identifier)  # If it's valid, this means it's an email
            user_filter = {'email': identifier}
        except ValidationError:
            if re.match(r"^\+?\d{10,15}$", identifier):
                user_filter = {'username': identifier}  # Assuming username stores the phone number
            else:
                messages.error(request, 'Please enter a valid email address')
                return redirect('forgot_password')

        if User.objects.filter(**user_filter).exists():
            user = User.objects.get(**user_filter)

            if 'email' in user_filter:
                mail_subject = "Reset Your Password"
                email_template = 'accounts/emails/reset_password_email.html'
                send_verification_email(request, user, mail_subject, email_template)
                messages.success(request, 'Password reset link has been sent to your email.')
            else:
                reset_link = request.build_absolute_uri(reverse('reset_password_validate', kwargs={
                    'uidb64': urlsafe_base64_encode(force_bytes(user.pk)),
                    'token': default_token_generator.make_token(user),
                }))
                whatsapp_message = f"Reset your password by clicking the link: {reset_link}"
                # send_whatsapp_message(identifier, whatsapp_message)  # Function to send WhatsApp messages
                messages.success(request, 'Password reset link has been sent to your WhatsApp number.')

            return redirect('login')
        else:
            messages.error(request, 'Account does not exist.')
            return redirect('forgot_password')

    return render(request, 'accounts/forgot_password.html')


def reset_password_validate(request, uidb64, token):
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = User._default_manager.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None
    
    if user is not None and default_token_generator.check_token(user, token):
        request.session['uid'] = uid
        messages.info(request, 'Please reset your password.')
        return redirect('reset_password')
    else:
        messages.error(request, 'This link has expired or is invalid.')
        return redirect('myAccount')



def reset_password(request):
    if request.method == 'POST':
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')

        
        if not password or not confirm_password:
            messages.error(request, "Both password fields are required.")
            return redirect('reset_password')


        if password != confirm_password:
            messages.error(request, "Passwords do not match.")
            return redirect('reset_password')


        try:
            validate_password(password)
        except ValidationError as e:
            for error in e.messages:
                messages.error(request, error)
            return redirect('reset_password')

        pk = request.session.get('uid')
        if not pk:
            messages.error(request, "Session expired. Please try resetting your password again.")
            return redirect('forgot_password')


        try:
            user = User.objects.get(pk=pk)
        except ObjectDoesNotExist:
            messages.error(request, "User does not exist.")
            return redirect('forgot_password')

        user.set_password(password)
        user.is_active = True 
        user.save()

        del request.session['uid']

        messages.success(request, 'Password reset successfully. You can now log in with your new password.')
        return redirect('login')

    return render(request, 'accounts/reset_password.html')




    
def newsletter_signup(request):
    if request.method == 'POST' and request.headers.get('x-requested-with') == 'XMLHttpRequest':
        email = request.POST.get('email')
        if email:
            if not Newsletter.objects.filter(email=email).exists():
                Newsletter.objects.create(email=email)
                return JsonResponse({'message': 'Done', 'status': 'success'})
            else:
                return JsonResponse({'message': 'This email is already subscribed.', 'status': 'error'})
        else:
            return JsonResponse({'message': 'Please enter a valid email address.', 'status': 'error'})

    return JsonResponse({'message': 'Invalid request', 'status': 'error'})


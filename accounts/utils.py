from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import EmailMessage
from django. conf import settings


def detectUser(user):
    if user.role == 1:
        redirectUrl = 'restaurantDashboard'
        return redirectUrl
    elif user.role == 2:
        redirectUrl = 'custDashboard'
        return redirectUrl
    elif user.role == None and user.is_superadmin:
        redirectUrl = '/admin'
        return redirectUrl
    else:
        redirectUrl =  'login'
        return redirectUrl
    

def send_verification_email(request, user, mail_subject,email_template, bcc=['aditya@orderzy.in']):
    from_email = settings.DEFAULT_FROM_EMAIL
    current_site = get_current_site(request)
    message = render_to_string(email_template,{
        'user':user,
        'domain':current_site,
        'uid': urlsafe_base64_encode(force_bytes(user.pk)),
        'token':default_token_generator.make_token(user),
    })
    to_email = user.email
    mail = EmailMessage(mail_subject, message,from_email,  to=[to_email],bcc=bcc)
    mail.content_subtype = "html"
    mail.send()
    
def send_notification(mail_subject, mail_template, context, bcc=['aditya@orderzy.in']):
    from_email = settings.DEFAULT_FROM_EMAIL
    message = render_to_string(mail_template, context)
    if(isinstance(context['to_email'], str)):
        to_email = []
        to_email.append(context['to_email'])
    else:
        to_email = context['to_email']
    mail = EmailMessage(mail_subject, message,from_email,  to=to_email,bcc=bcc)
    mail.content_subtype = "html"
    mail.send()
    
    

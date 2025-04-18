from django.db import models
from accounts.models import User, UserProfile
from accounts.utils import send_notification
from datetime import  date, datetime
from django.db import models
from django.contrib.gis.db import models as gismodels
from django.contrib.gis.geos import Point
from django.db.models.signals import post_save
from django.dispatch import receiver
from .utils import generate_qr
from django.utils.text import slugify
from django.contrib.sites.models import Site
import os
from django.conf import settings
class FoodHub(models.Model):
    foodhub_name = models.CharField(max_length=100)
    latitude = models.CharField(max_length=20, blank=True, null=True)
    longitude = models.CharField(max_length=20, blank=True, null=True)
    location = gismodels.PointField(blank=True, null=True, srid=4326)

    def save(self, *args, **kwargs):
        if self.latitude and self.longitude:
            self.location = Point(float(self.longitude), float(self.latitude))
        super(FoodHub, self).save(*args, **kwargs)

    def __str__(self):
        return self.foodhub_name

class Restaurant(models.Model):
    user = models.OneToOneField(User, related_name='user', on_delete=models.CASCADE)
    user_profile = models.OneToOneField(UserProfile, related_name='userprofile', on_delete=models.CASCADE)
    restaurant_name = models.CharField(max_length=50)
    restaurant_slug = models.SlugField(max_length=100, unique=True)
    is_approved = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)
    food_hub = models.ForeignKey(FoodHub, on_delete=models.SET_NULL, null=True, blank=True)
    menu_url = models.URLField(default='https://default.url')

    @property
    def qr_code_path(self):
        return f'{self.id}_menu_qr.png'


    
    def __str__(self):
        return self.restaurant_name


    def is_open(self):
        today = date.today().isoweekday()

        current_opening_hours = OpeningHour.objects.filter(restaurant=self, day=today)

        now = datetime.now().time()
        for opening_hour in current_opening_hours:
            if not opening_hour.is_closed:
                start = opening_hour.from_hour
                end = opening_hour.to_hour

                if start < end:
                    if start <= now <= end:
                        return True
                else:
                    if now >= start or now <= end:
                        return True

        return False


    
    
    def save(self, *args, **kwargs):
        if not self.pk: 
            self.restaurant_slug = slugify(self.restaurant_name) + '-' + str(self.user.id)
        
        current_site = Site.objects.get_current()
        
        self.menu_url = f"{current_site.domain}/marketplace/{self.restaurant_slug}/"
        
        if self.pk is not None:
            orig = Restaurant.objects.get(pk=self.pk)
            if orig.is_approved != self.is_approved:
                mail_template = 'accounts/emails/admin_approval_email.html'
                context = {
                        'user': self.user,
                        'is_approved': self.is_approved,
                        'to_email':self.user.email,
                    }
                if self.is_approved == True:
                    mail_subject = "Congrats, Your Restaurant has been approved"
                    send_notification(mail_subject, mail_template, context)
                else:
                    mail_subject = "We're Sorry!, You are not eligible for publishing your restaurant on our marketplace."
                    send_notification(mail_subject, mail_template, context)
        return super(Restaurant, self).save(*args, **kwargs)
    


@receiver(post_save, sender=Restaurant)
def generate_qr_code(sender, instance, created, **kwargs):
    filename = instance.qr_code_path
    file_path = os.path.join(settings.BASE_DIR, 'orderzy', 'static', 'qr_codes', filename)
    print("filename",filename)
    print("file_path",file_path)
    
    if not os.path.exists(file_path):
        print(f"QR code file is missing. Generating QR for: {instance.restaurant_name} with URL: {instance.menu_url}")
        generate_qr(instance.menu_url, filename)
    else:
        print(f"QR code already generated for {instance.restaurant_name}. No change to menu URL.")




        
DAYS = [
    (1,("Monday")),
    (2,("Tuesday")),
    (3,("Wednesday")),
    (4,("Thursday")),   
    (5,("Friday")),
    (6,("Saturday")),
    (7,("Sunday")),

]

class OpeningHour(models.Model):
    restaurant = models.ForeignKey(Restaurant, on_delete=models.CASCADE)
    day=models.IntegerField(choices=DAYS)
    from_hour = models.TimeField(blank=True, null=True)
    to_hour = models.TimeField(blank=True, null=True)
    is_closed = models.BooleanField(default=False)
    
    class Meta:
        ordering = ('day','-from_hour')
        unique_together = ('restaurant','day','from_hour','to_hour')
        
        
        
    def __str__(self):
        return self.get_day_display()
    

class SeatingPlan(models.Model):
    restaurant = models.OneToOneField(Restaurant, on_delete=models.CASCADE, related_name='seating_plan')
    seating_plan_available = models.BooleanField(default=False)
    tables_for_two = models.IntegerField(default=0)
    tables_for_four = models.IntegerField(default=0)
    tables_for_six = models.IntegerField(default=0)

    def __str__(self):
        return f"Seating Plan for {self.restaurant.restaurant_name}"

    







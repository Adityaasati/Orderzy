from django.db import models
from django.db.models.fields.related import  OneToOneField
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
from django.contrib.gis.db import models as gismodels
from django.contrib.gis.geos import Point



class UserManager(BaseUserManager):
    def create_user(self, first_name, last_name, username, email=None,phone_number=None, password=None,**extra_fields):
        if not username:
            raise ValueError('Username is required')
        if not password:
            raise ValueError('Password is required')
        
        if '@' in username:
            email = self.normalize_email(username)
            phone_number = None
        else:
            email = None
            phone_number = username
        
        user = self.model(
            first_name=first_name,
            last_name=last_name,
            username=username,
            email=email,
            phone_number=phone_number,
            **extra_fields
        )
        user.set_password(password)
        user.save(using=self._db)
        return user
        
    
    
    def create_superuser(self, first_name, last_name, username, email=None,phone_number=None, password=None, **extra_fields):
        user = self.create_user(
            first_name=first_name,
            last_name=last_name,
            username=username,
            password=password,
            **extra_fields
        )
        user.is_admin=True
        user.is_active = True
        user.is_staff = True
        user.is_superadmin = True
        user.is_superuser = True
        user.save(using=self._db)
        return user


class User(AbstractBaseUser):
    
    RESTAURANT = 1
    CUSTOMER = 2
 
    
    ROLE_CHOICE = (
        (RESTAURANT, 'Restaurant'),
        (CUSTOMER, 'Customer')

        
    )
    
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    username = models.CharField(max_length=50, unique=True)
    email = models.EmailField(max_length=100, unique=True, blank=True, null=True)
    phone_number = models.CharField(max_length=12, blank=True, null=True)
    role = models.PositiveSmallIntegerField(choices=ROLE_CHOICE, blank=True, null=True)
    
    #required fields
    date_joined = models.DateTimeField(auto_now_add=True)
    last_login = models.DateTimeField(auto_now_add=True)
    created_date = models.DateTimeField(auto_now_add=True)
    modified_date = models.DateTimeField(auto_now=True)
    is_admin = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=False)
    is_superadmin = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False) 

 
    USERNAME_FIELD = 'username' 
    REQUIRED_FIELDS = ['first_name', 'last_name']
    
    objects = UserManager()

    def __str__(self):
        return self.username
    
    def save(self, *args, **kwargs):
        if '@' in self.username:
            self.email = self.username
            self.phone_number = None
        else:
            self.email = None
            self.phone_number = self.username

        super(User, self).save(*args, **kwargs)
    
    def has_perm(self,perm, obj=None):
        return self.is_admin
    
    def has_module_perms(self,app_label):
        return True
    
    def get_role(self):
        if self.role == 1:
            user_role = 'Restaurant'
        elif self.role == 2:
            user_role = 'Customer'
        return user_role
    def get_full_name(self):
        return f"{self.first_name} {self.last_name}".strip()
    


class UserProfile(models.Model):
    user = OneToOneField(User, on_delete=models.CASCADE, blank=True, null = True)
    profile_picture = models.ImageField(upload_to='users/profile_pictures', blank=True, null = True)
    cover_photo = models.ImageField(upload_to='users/cover_photos', blank=True, null = True)
    address = models.CharField(max_length=250, blank=True, null = True)
    country = models.CharField(max_length=15, blank=True, null = True)
    state = models.CharField(max_length=15, blank=True, null = True)
    city = models.CharField(max_length=15, blank=True, null = True)
    pin_code = models.CharField(max_length=6, blank=True, null = True)
    latitude = models.CharField(max_length=20, blank=True, null = True)
    longitude = models.CharField(max_length=20, blank=True, null = True)
    location = gismodels.PointField(blank=True, null=True, srid=4326)
    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)
    

    
    def __str__(self):
        if self.user:
            return self.user.username or 'No username'
        return 'No user'
    
    def save(self, *args, **kwargs):
        if self.latitude and self.longitude:
            self.location = Point(float(self.longitude), float(self.latitude))
            return super(UserProfile, self).save(*args, **kwargs)
        return super(UserProfile, self).save(*args, **kwargs)
    
    # models.py


class ContactMessage(models.Model):
    user = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL)
    name = models.CharField(max_length=100)
    message = models.TextField()
    sent_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Message from {self.name} at {self.sent_at}"



class Newsletter(models.Model):
    email = models.EmailField(unique=True)
    date_subscribed = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.email

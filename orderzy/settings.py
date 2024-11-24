
from django.contrib.messages import constants as messages
from cashfree_pg.api_client import Cashfree
from pathlib import Path
from decouple import config
import os
import logging
from logging.handlers import TimedRotatingFileHandler, RotatingFileHandler


# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


logger = logging.getLogger('django')
logs_dir = os.path.join(BASE_DIR, 'logs')
if not os.path.exists(logs_dir):
    os.makedirs(logs_dir)

SECRET_KEY = config('SECRET_KEY')


DEBUG = config('DEBUG', cast=bool)

ALLOWED_HOSTS = ['139.59.2.143','127.0.0.1','orderzy.in','www.orderzy.in', '2346-152-58-56-32.ngrok-free.app']

CSRF_TRUSTED_ORIGINS = [
    'https://2346-152-58-56-32.ngrok-free.app ', 'https://www.orderzy.in','https://orderzy.in'
]

# Application definition

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django.contrib.sites",
    "django.contrib.sitemaps",
    "accounts",
    "restaurant",
    "menu",
    "marketplace",
    "customers",
    "orders",
    "django.contrib.gis",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "orders.request_object.RequestObjectMiddleware", #custom middleware
]

ROOT_URLCONF = "orderzy.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": ['templates'],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                "accounts.context_processors.get_restaurant",
                "accounts.context_processors.get_google_api",
                "marketplace.context_processors.get_cart_counter",
                "marketplace.context_processors.get_cart_amounts",
                "accounts.context_processors.get_user_profile",
                "accounts.context_processors.get_paypal_client_id",
                
            ],
        },
    },
]

WSGI_APPLICATION = "orderzy.wsgi.application"




DATABASES = {
    "default": {
        # "ENGINE": "django.db.backends.postgresql",
        "ENGINE": "django.contrib.gis.db.backends.postgis",
        "NAME": config('DB_NAME'),
        "USER": config('DB_USER'),
        "PASSWORD":config('DB_PASSWORD'),
        "HOST":config('DB_HOST'),
        "PORT": "5432", 
    }
}

AUTHENTICATION_BACKENDS = [
    'accounts.auth_backends.EmailOrPhoneAuthBackend',
    'django.contrib.auth.backends.ModelBackend',
]


AUTH_USER_MODEL = 'accounts.User'
# Password validation
# https://docs.djangoproject.com/en/5.0/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]


# Internationalization
# https://docs.djangoproject.com/en/5.0/topics/i18n/

LANGUAGE_CODE = "en-us"

TIME_ZONE = 'Asia/Kolkata'

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.0/howto/static-files/

STATIC_URL = "/static/"
STATIC_ROOT = BASE_DIR/'static'
STATICFILES_DIRS = [
    'orderzy/static'
]



SITE_ID = 1 

MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR/'media'

# Default primary key field type
# https://docs.djangoproject.com/en/5.0/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"




MESSAGE_TAGS = {
    messages.ERROR:'danger',
}

#Email Configurations

EMAIL_HOST = config('EMAIL_HOST')
EMAIL_PORT = config('EMAIL_PORT', cast=int)
EMAIL_HOST_USER = config('EMAIL_HOST_USER')
EMAIL_HOST_PASSWORD = config('EMAIL_HOST_PASSWORD')
EMAIL_USE_SSL = config('EMAIL_USE_SSL', cast=bool)
DEFAULT_FROM_EMAIL = 'Orderzy <aditya@orderzy.in>'


GOOGLE_API_KEY = 'AIzaSyBzaYo0Lsv_1yGGLJhMIlDHwsEZ0DuhdCI'

gdal_dll_path = str(BASE_DIR / 'env' / 'Lib' / 'site-packages' / 'osgeo' / 'gdal.dll')

if DEBUG == True:
    os.environ['PATH'] = str(BASE_DIR / 'env' / 'Lib' / 'site-packages' / 'osgeo') + ';' + os.environ['PATH']
    os.environ['PROJ_LIB'] = str(BASE_DIR / 'env' / 'Lib' / 'site-packages' / 'osgeo' / 'data' / 'proj')
    GDAL_LIBRARY_PATH = gdal_dll_path



PAYPAL_CLIENT_ID = config('PAYPAL_CLIENT_ID')
CASHFREE_X_CLIENT_ID = config('CASHFREE_XCLIENTID')
CASHFREE_X_CLIENT_SECRET = config('CASHFREE_XCLIENTSECRET')
CASHFREE_X_ENVIRONMENT = config('CASHFREE_XENVIRONMENT', default='SANDBOX')  # Default to 'TEST' if not set
X_API_VERSION = config('X_API_VERSION')
SECURE_CROSS_ORIGIN_OPENER_POLICY = 'same-origin-allow-popups'


SESSION_COOKIE_AGE = 3600 * 24  
SESSION_SAVE_EVERY_REQUEST = True 



if DEBUG:
    SESSION_COOKIE_DOMAIN = None  # Use the domain of the request (localhost)
    SESSION_COOKIE_SECURE = False
    SESSION_COOKIE_SAMESITE = None
    SESSION_COOKIE_HTTPONLY = True
else:
    SESSION_COOKIE_DOMAIN = ".orderzy.in"
    SESSION_COOKIE_SECURE = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    SESSION_COOKIE_HTTPONLY = True


LOG_FILE_PATH = os.path.join(logs_dir, 'django.log') if DEBUG else '/var/log/orderzy.log'


# Logging Configuration
LOGGING = {
    'version': 1,
    'disable_existing_loggers': True,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'file': {
            'class': 'logging.handlers.TimedRotatingFileHandler',
            'filename': LOG_FILE_PATH,
            'when': 'midnight',
            'backupCount': 7,
            'formatter': 'verbose',
            'encoding': 'utf-8',
        },
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['file'] if not DEBUG else ['file', 'console'],
            'level': 'DEBUG' if DEBUG else 'INFO',
            'propagate': False,
        },
        'django.server': {
            'handlers': ['file'],
            'level': 'INFO',
            'propagate': False,
        },
        'django.db.backends': {
            'handlers': ['file'],
            'level': 'ERROR',
            'propagate': False,
        },
        'root': {
            'handlers': ['file'],
            'level': 'WARNING',
        },
    },
}

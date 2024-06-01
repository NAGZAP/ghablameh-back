from datetime import timedelta
from pathlib import Path
from environ import Env

env = Env()
Env.read_env()

VERSION  = "1"
BASE_URL = f"api/v{VERSION}"

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = env("SECRET_KEY")

DEBUG = True

USE_X_FORWARDED_HOST = True

SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

ALLOWED_HOSTS = ['*']

INTERNAL_IPS  = ["127.0.0.1"]

INSTALLED_APPS = [
    'jazzmin',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django_filters',
    
    'rest_framework',
    'drf_yasg',
    'channels',
    
    'core',
    'food_reservation',
    'notifications',
    'wallets',
]

MIDDLEWARE = [
    'core.middleware.corsheaders.CorsMiddlewareDjango',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'ghablameh.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'ghablameh.wsgi.application'

DATABASES = {
    'default': {
        'ENGINE': env("DB_ENGINE"),
        'NAME': env("DB_NAME"),
        'USER': env("DB_USER"),
        'PASSWORD': env("DB_PASSWORD"),
        'HOST': env("DB_HOST"),
        'PORT': env("DB_PORT"),
    }
}


AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'Asia/Tehran'

USE_I18N = True

USE_TZ = True


STATIC_URL = f'api/v{VERSION}/static/'

STATIC_ROOT = "/var/www/ghablameh/static"

MEDIA_URL = f'api/v{VERSION}/media/'

MEDIA_ROOT = "/var/www/ghablameh/media"


DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

AUTH_USER_MODEL = 'core.User'

ASGI_APPLICATION = 'ghablameh.routing.application'


EMAIL_BACKEND = env("EMAIL_BACKEND")
EMAIL_HOST = env("EMAIL_HOST")
EMAIL_PORT = env("EMAIL_PORT")
EMAIL_USE_TLS = env("EMAIL_USE_TLS")
EMAIL_HOST_USER = env("EMAIL_HOST_USER")
EMAIL_HOST_PASSWORD = env("EMAIL_HOST_PASSWORD")

SIMPLE_JWT = {
    "AUTH_HEADER_TYPES" : ('JWT',),
    "ACCESS_TOKEN_LIFETIME": timedelta(days=30),
    "REFRESH_TOKEN_LIFETIME": timedelta(days=300),
}



REST_FRAMEWORK = {
    
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ),

}

LOGGING ={
    'version':1,
    'disable_existing_loggers':False,
    'handlers':{
        'console':{
            'class':'logging.StreamHandler'
        },
        'file':{
            'class':'logging.FileHandler',
            'filename':'general.log',
            'formatter': 'verbose'
        }
    },
    'loggers':{
        '':{
            'handlers':['file','console'],
            'level':'INFO'
        }
    },
    'formatters':{
        'verbose':{
            'format':'{asctime} ({levelname}) - {name} - {message}',
            'style' :'{'
        }

    }
}

SWAGGER_SETTINGS = {
    'SECURITY_DEFINITIONS': {
        'Bearer': {
            'type': 'apiKey',
            'name': 'Authorization',
            'in': 'header'
        }
    },
}

JAZZMIN_SETTINGS = {
    "site_title": "Ghablameh",
    "site_brand": "Ghablameh Administration",
    "site_logo": "core/img/logo.png",
    "custom_css": "core/css/custom.css",
    "welcome_sign": "Welcome to Ghablameh Admin panel",
    "copyright": "NAGZAP",
    "related_modal_active": True,
    "topmenu_links": [

        {"name": "Home",  "url": "admin:index", "permissions": ["auth.view_user"]},

        {"name": "Github", "url": "https://github.com/NAGZAP/ghablameh-back"},

        {"app": "food_reservation", "name": "Reservation"},
    ],
    "icons": {
        "core": "fas fa-users-cog",
        "core.user": "fas fa-user",
        "auth.Group": "fas fa-users",
        "store": "fas fa-store",
        "store.Plant": "fas fa-leaf",
        "store.Order": "fas fa-shopping-cart",
        "store.Accessory": "fas fa-dolly",
        "store.Category": "fas fa-stream",
        "store.Product": "fas fa-seedling",
    },
}


CHANNEL_LAYERS = {
    "default": {
        "BACKEND": "channels.layers.InMemoryChannelLayer",
    },
}

PGW_API_URL = env("PGW_API_URL")
PGW_URL = env("PGW_URL")
PWG_ACCEPTOR_CODE = env("PGW_ACCEPTOR_CODE")
PGW_PASSWORD = env("PGW_PASSWORD")
PGW_CALL_BACK_URL = env("PGW_CALL_BACK_URL")
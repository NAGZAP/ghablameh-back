from datetime import timedelta
from pathlib import Path
from environ import Env

env = Env()
Env.read_env()

VERSION = "1"

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = env("SECRET_KEY")

DEBUG = False

USE_X_FORWARDED_HOST = True

SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

ALLOWED_HOSTS = ['*']

INTERNAL_IPS  = ["127.0.0.1"]

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    
    'rest_framework',
    'drf_yasg',
    
    'core',
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

"""
Django settings for shout_app project.

Generated by 'django-admin startproject' using Django 2.2.

For more information on this file, see
https://docs.djangoproject.com/en/2.2/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/2.2/ref/settings/
"""

import os
import django_heroku

django_heroku.settings(locals)

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
# BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/2.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
#- SECRET_KEY='qo&pp(lwt1=rl&zip_dc=tjw9wrbit7i2xr+v=8u&mxw$o+ym2'
SECRET_KEY = os.getenv('SECRET_KEY', 'qo&pp(lwt1=rl&zip_dc=tjw9wrbit7i2xr+v=8u&mxw$o+ym2')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG =  os.environ.get('DJANGO_DEBUG', '') != 'False'

ALLOWED_HOSTS = ['0.0.0.0',
        'theshoutit.herokuapp.com']


# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.sites',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'master',
    'rest_framework',
    'allauth',
    'allauth.account',
    'allauth.socialaccount',
]
SITE_ID = 1

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
]

ROOT_URLCONF = 'shout_app.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates'), os.path.join(BASE_DIR,'templates', 'allauth')],
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

WSGI_APPLICATION = 'shout_app.wsgi.application'


# Database
# https://docs.djangoproject.com/en/2.2/ref/settings/#databases
DATABASES = {
    'default': {
        'ENGINE': os.getenv('SQL_ENGINE'),
        'NAME': os.getenv('SQL_DATABASE'),
        'USER': os.getenv('SQL_USER'),
        'PASSWORD': os.getenv('SQL_PASSWORD'),
        'HOST': os.getenv('SQL_HOST'),
        'PORT': os.getenv('SQL_PORT')
    }
}

# USER CLASS
AUTH_USER_MODEL = 'master.CustomUser'

# Password validation
# https://docs.djangoproject.com/en/2.2/ref/settings/#auth-password-validators

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

# Django AuthALL
ACCOUNT_EMAIL_CONFIRMATION_EXPIRE_DAYS =1
ACCOUNT_EMAIL_REQUIRED = None
ACCOUNT_EMAIL_VERIFICATION = "optional"
ACCOUNT_LOGIN_ATTEMPTS_LIMIT = 5
ACCOUNT_LOGIN_ATTEMPTS_TIMEOUT = 86400 # 1 day in seconds
ACCOUNT_LOGOUT_REDIRECT_URL ='/'
LOGIN_REDIRECT_URL = 'master:home' 

AUTHENTICATION_BACKENDS = (
    'django.contrib.auth.backends.ModelBackend',
    'allauth.account.auth_backends.AuthenticationBackend',
)

ACCOUNT_FORMS = {
    'signup': 'master.forms.SignUpForm',
}
# EMAIL CLIENT
EMAIL_USE_TLS = True
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_HOST_USER = DEFAULT_FROM_EMAIL = 'tifyspott80@gmail.com'
EMAIL_HOST_PASSWORD = 'random'
# Internationalization
# https://docs.djangoproject.com/en/2.2/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/2.2/howto/static-files/
STATIC_URL = '/staticfiles/'
STATICFILES_DIRS = (os.path.join(BASE_DIR, 'staticfiles'), )

# Media
MEDIA_URL = '/mediafiles/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'mediafiles')

# Redirects
LOGIN_URL = 'account_login'
LOGIN_REDIRECT_URL = 'home'
LOGOUT_REDIRECT_URL = 'home'

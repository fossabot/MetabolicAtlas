"""
Django settings for metabolicatlas project.
Generated by 'django-admin startproject' using Django 1.10.5.
For more information on this file, see
https://docs.djangoproject.com/en/1.10/topics/settings/
For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.10/ref/settings/
"""

import os

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.10/howto/deployment/checklist/

SECRET_KEY = os.getenv('DJANGO_KEY')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = os.getenv('DJANGO_IS_DEBUG') == 'True'

ALLOWED_HOSTS = [
    'localhost',
    'icsb.chalmers.se',
    'metabolicatlas.sysbio.chalmers.se',
    'metabolicatlas.org',
    'www.metabolicatlas.org',
]

# Application definition
INSTALLED_APPS = [
    'django.contrib.staticfiles',
    'django.contrib.postgres',
    'rest_framework',
    'rest_framework_swagger',
    'api',
    'corsheaders',
    'django_extensions',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_BROWSER_XSS_FILTER = True
CSRF_COOKIE_SECURE = True
X_FRAME_OPTIONS = 'DENY'

ROOT_URLCONF = 'metabolicatlas.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': ['metabolicatlas/templates/'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
            ],
        },
    },
]

WSGI_APPLICATION = 'metabolicatlas.wsgi.application'

# Database https://docs.djangoproject.com/en/1.10/ref/settings/#databases
DATABASES = {
    'default': {
        # 'ENGINE': 'django.db.backends.postgresql',
        # 'NAME': 'hmr2',
        # 'USER': os.getenv('POSTGRES_USER'),
        # 'PASSWORD': os.getenv('POSTGRES_PASSWORD'),
        # 'HOST': 'db',
        # 'PORT': 5432,
    },
    'human1': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'human1',
        'USER': os.getenv('POSTGRES_USER'),
        'PASSWORD': os.getenv('POSTGRES_PASSWORD'),
        'HOST': 'db',
        'PORT': 5432,
    },
    'yeast8': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'yeast8',
        'USER': os.getenv('POSTGRES_USER'),
        'PASSWORD': os.getenv('POSTGRES_PASSWORD'),
        'HOST': 'db',
        'PORT': 5432,
    },
    'gems': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'gems',
        'USER': os.getenv('POSTGRES_USER'),
        'PASSWORD': os.getenv('POSTGRES_PASSWORD'),
        'HOST': 'db',
        'PORT': 5432,
    }
}

# Database routers
DATABASE_ROUTERS = [
    'api.routers.GemodelRouter',
    'api.routers.ApiRouter'
]

# CORS https://github.com/ottoyiu/django-cors-headers
CORS_ORIGIN_WHITELIST = (
    'http://localhost',
    'https://icsb.chalmers.se',
    'https://metabolicatlas.org',
    'https://www.metabolicatlas.org',
)

# SWAGGER
SWAGGER_SETTINGS = {
    'USE_SESSION_AUTH': False,
    'SECURITY_DEFINITIONS': {
        'basic': {
            'type': 'basic'
        }
    },
}

REST_FRAMEWORK = {
    'DEFAULT_VERSIONING_CLASS': 'rest_framework.versioning.QueryParameterVersioning',
    'DEFAULT_AUTHENTICATION_CLASSES': [],
    'DEFAULT_PERMISSION_CLASSES': [],
    'UNAUTHENTICATED_USER': None,
}

# Internationalization https://docs.djangoproject.com/en/1.10/topics/i18n/
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_L10N = True
USE_TZ = True

STATIC_URL = '/static/'
STATIC_ROOT = './static/'

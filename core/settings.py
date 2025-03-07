import os
from pathlib import Path
from dotenv import load_dotenv
from django.utils.translation import gettext_lazy as _


load_dotenv('.env')

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/5.0/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.getenv('SECRET_KEY')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ["www.libsmart.uz","libsmart.uz","3.86.157.16","127.0.0.1", "localhost"]

# Application definition

INSTALLED_APPS = [
    'jazzmin',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'rosetta',
    'django.contrib.staticfiles',
    'lib.apps.LibConfig',
    'users.apps.UsersConfig',
    'django.contrib.sites',
    'rest_framework',
    'modeltranslation',
    'storages',  # ✅ django-storages ni yoqish
    'corsheaders',


]

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.locale.LocaleMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'core.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
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

WSGI_APPLICATION = 'core.wsgi.application'

# Database
# https://docs.djangoproject.com/en/5.0/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}
# DATABASES = {
#     'default': {
#         'ENGINE': 'django.db.backends.postgresql',  # Yoki 'django.db.backends.mysql' MySQL uchun
#         'NAME': 'library',  # AWS RDS da yaratganingizni yozing
#         'USER': 'postgres',  # AWS RDS da tanlagan username
#         'PASSWORD': 'Abduqodir2025',  # AWS RDS paroli
#         'HOST': 'library.cqdqcq8e0noq.us-east-1.rds.amazonaws.com',  # AWS RDS endpoint
#         'PORT': '5432',  # PostgreSQL uchun, MySQL bo‘lsa '3306'
#     }
# }

# Password validation
# https://docs.djangoproject.com/en/5.0/ref/settings/#auth-password-validators

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

# Internationalization
# https://docs.djangoproject.com/en/5.0/topics/i18n/

LANGUAGE_CODE = 'uz'

LANGUAGES = (
    ('uz', _('Uzbek')),
    ('en', _('English')),
    ('ru', _('Russian'))
)

LOCALE_PATHS = (
    os.path.join(BASE_DIR, "locale/"),
)

MODELTRANSLATION_DEFAULT_LANGUAGE = 'uz'


TIME_ZONE = 'Asia/Tashkent'

USE_I18N = True

USE_L10N = True

USE_TZ = True

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.0/howto/static-files/

STATIC_URL = '/static/'
STATICFILES_DIRS = [
    BASE_DIR / 'static',
]
STATIC_ROOT = BASE_DIR / 'staticfiles'

MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

# settings.py dagi AWS media saqlash sozlamalari
DEFAULT_FILE_STORAGE = 'django.core.files.storage.FileSystemStorage'  # Agar AWS S3 ishlatilmasa


# Default primary key field type
# https://docs.djangoproject.com/en/5.0/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
AUTH_USER_MODEL = 'users.User'
SITE_ID = 1
LOGIN_REDIRECT_URL = 'main'

CORS_ALLOW_ORIGINS = [
    '*.ngrok-free.app',
    'https://example.com',
]
CSRF_TRUSTED_ORIGINS = ['http://127.0.0.1', 'http://localhost']
CSRF_COOKIE_SECURE = False

# email settings

EMAIL_HOST = os.getenv('EMAIL_HOST')
EMAIL_USE_TLS = True
EMAIL_PORT = 587
EMAIL_HOST_USER = os.getenv('EMAIL_HOST_USER')
EMAIL_HOST_PASSWORD = os.getenv('EMAIL_HOST_PASSWORD')

# Authentication settings
AUTHENTICATION_BACKENDS = [
    'users.backends.EmailBackend',
]

# Celery settings
CELERY_BROKER_URL = 'redis://localhost:6379'
CELERY_RESULT_BACKEND = 'redis://localhost:6379'
broker_connection_retry_on_startup = True

LOGIN_URL = "login"
LOGOUT_URL = "logout"


AWS_ACCESS_KEY_ID = os.getenv("AWS_ACCESS_KEY_ID")
AWS_SECRET_ACCESS_KEY = os.getenv("AWS_SECRET_ACCESS_KEY")
AWS_STORAGE_BUCKET_NAME = os.getenv("AWS_STORAGE_BUCKET_NAME")  # 🎯 **AWS Bucket nomingiz**
AWS_REGION = os.getenv("AWS_REGION", "us-east-1")  # ✅ Default: us-east-1
AWS_REKOGNITION_COLLECTION = os.getenv("AWS_REKOGNITION_COLLECTION", "face-id-collection")

# 🎯 AWS media fayllarni saqlash
DEFAULT_FILE_STORAGE = "storages.backends.s3boto3.S3Boto3Storage"
AWS_S3_ADDRESSING_STYLE = "path"  # 🎯 **URL'ni to‘g‘ri shaklda ishlatish**
AWS_QUERYSTRING_AUTH = False  # 🎯 **Har bir fayl URL'ni imzo qo‘yishsiz ishlatish**

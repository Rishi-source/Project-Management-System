PASSWORD = '1234'
import os
from django.core.management.utils import get_random_secret_key
DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BASE_DIR = DIR
SECRETKEY = get_random_secret_key
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [
            # Add custom template directories if needed
            os.path.join(BASE_DIR, 'templates'),
        ],
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
APPS =  [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'crispy_forms',
    'widget_tweaks',
    'employees',
    'wkhtmltopdf',
    'employees.templatetags',
]
PACK = 'bootstrap4'
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]
ROOT = 'pms.urls'
PASSWORD_VAL =  [
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
EMAIL = 'django.db.models.BigAutoField'
DATABASE_INFO = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'PMS', 
        'USER': 'postgres',
        'PASSWORD': PASSWORD , 
        'HOST': '127.0.0.1', 
        'PORT': '5432',
    }
}
TZ = 'Asia/Kolkata'
LANG = 'en-us'
WSGI = 'pms.wsgi.application'
EMAIL_END =  'django.core.mail.backends.console.EmailBackend'
MEDIA = '/media/'
STATIC = '/static/'
STATIC_R = os.path.join(BASE_DIR, 'staticfiles')
STATIC_DIRS = (
    os.path.join(BASE_DIR, 'static'),
)

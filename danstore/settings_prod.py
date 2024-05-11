import os

DEBUG = False
ALLOWED_HOSTS = ['18.217.48.125']

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.environ.get('DBNAME'),
        'USER': os.environ.get('DBUSER'),
        'PASSWORD': os.environ.get('DBPASS'),
        'HOST': os.environ.get('DBHOST', '127.0.0.1'),
        'PORT': os.environ.get('DBPORT', '5432'),
    }
}

STATIC_ROOT = 'static'

STATICFILES_DIRS = ['static_source']

STATIC_URL = 'static/'

MEDIA_ROOT = 'media'

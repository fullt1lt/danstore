import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
# Database
# https://docs.djangoproject.com/en/5.0/ref/settings/#databases

if os.getenv('GITHUB_WORKFLOW'):
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.postgresql',
            'NAME': 'github-actions',
            'USER': 'postgres',
            'PASSWORD': 'postgres',
            'HOST': 'localhost',
            'PORT': '5432'
        }
    }
else:

    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": BASE_DIR / "db.sqlite3",
            "TEST": {
                "NAME": BASE_DIR / "db.sqlite3",
            },
        }
    }


DEBUG = True

ALLOWED_HOSTS = []

STATIC_ROOT = 'static_final'
STATICFILES_DIRS = ['static_source']

STATIC_URL = 'static/'

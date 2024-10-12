import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
SECRET_KEY = 'django-insecure-(*81e%goasf9@=pn2^(a%*6rgg$fp3b6c203jkahodmrl!=6%v'
DEBUG = True

ALLOWED_HOSTS = []

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

STATIC_DIR = os.path.join(BASE_DIR, 'static')
if DEBUG:
    STATICFILES_DIRS = [os.path.join(BASE_DIR, 'static')]
else:
    STATIC_ROOT = os.path.join(BASE_DIR, 'static')
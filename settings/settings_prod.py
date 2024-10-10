import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
SECRET_KEY = 'django-insecure-(*81e%goasf9@=pn2^(a%*6rgg$fp3b6c203jkahodmrl!=6%v'
DEBUG = False

ALLOWED_HOSTS = ['127.0.0.1', '78.107.233.196', '192.168.1.111', 'www.asusrm.ru', 'asusrm.ru']
# CSRF_TRUSTED_ORIGINS = ['http://www.asusrm.ru', 'http://asusrm.ru', 'asusrm.ru', '127.0.0.1', '78.107.233.196',
#                         '192.168.1.111']
INTERNAL_IPS = [
    # ...
    "127.0.0.1",
    # ...
]

# Указывает браузерам отправлять куки только через защищенное HTTPS-соединение
SESSION_COOKIE_SECURE = False
CSRF_COOKIE_SECURE = False
# Указывает Django использовать безопасные куки
SECURE_BROWSER_XSS_FILTER = False
SECURE_CONTENT_TYPE_NOSNIFF = False

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}
# DATABASES = {
#     'default': {
#         'ENGINE': 'django.db.backends.postgresql_psycopg2',
#         'NAME': 'ga-helper',
#         'USER': 'admin',
#         'PASSWORD': 'r2t2j35k',
#         'HOST': '127.0.0.1',
#         'PORT': '5432',
#     }
# }
#
STATIC_DIR = os.path.join(BASE_DIR, 'static')
if DEBUG:
    STATICFILES_DIRS = [os.path.join(BASE_DIR, 'static')]
else:
    STATIC_ROOT = os.path.join(BASE_DIR, 'static')
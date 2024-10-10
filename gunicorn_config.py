command = '/home/asusrm/djangoapps/parser/env/bin/gunicorn/'
pythonpath = '/home/asusrm/djangoapps/parser/siteparser'
bind = '127.0.0.1:8001'
workers = 3
user = 'asusrm'
limit_request_fields = 32000
limit_request_fields_size = 0
raw_env = 'DJANGO_SETTINGS_MODULE = asuSrm.settings'
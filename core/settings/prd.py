"""Production settings and globals."""
import sys
import os
from os import environ
from .base import *

# Import secrets
sys.path.append(
    os.path.normpath(os.path.join(
        PROJECT_ROOT, '../secrets/{{ project_name }}/prd'))
)
from django_settings import *

STATIC_URL = 'https://s3.amazonaws.com/media.knightlab.com/{{ project_name }}/'
DEBUG = False
ALLOWED_HOSTS = [
    '.knightlab.com',   # Allow domain and subdomains
    '.knightlab.com.',  # Also allow FQDN and subdomains
]

# should these be in site.py?
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = environ.get('EMAIL_HOST', 'smtp.gmail.com')
EMAIL_HOST_PASSWORD = environ.get('EMAIL_HOST_PASSWORD', '')
EMAIL_HOST_USER = environ.get('EMAIL_HOST_USER', 'knightlab@northwestern.edu')
EMAIL_PORT = environ.get('EMAIL_PORT', 587)
EMAIL_SUBJECT_PREFIX = '[{{ project_name }}] '
EMAIL_USE_TLS = True
SERVER_EMAIL = EMAIL_HOST_USER

DATABASES = {
    'default': {
        'ENGINE': '',
        'NAME': '',
        'USER': '',
        'PASSWORD': '',
        'HOST': '',
        'PORT': '',
        'ROOT_USER': '', # for mysql
        'ROOT_PASSWORD': '' # for mysql
    }
}

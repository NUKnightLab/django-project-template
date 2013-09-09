"""settings.loc is intended to be a shared local settings file that is to
be used for development environments. If you have user-specific settings, 
please put them in a <username>.py file that imports the local settings. See
the user.py example.
"""
from .base import *

DEBUG = True
TEMPLATE_DEBUG = DEBUG
EMAIL_HOST = 'localhost'
EMAIL_PORT = 1025

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': 'db',
        'USER': '',
        'PASSWORD': '',
        'HOST': 'localhost',
        'PORT': '',
        'ROOT_USER': '', # for mysql
        'ROOT_PASSWORD': '' # for mysql
    }
}

INSTALLED_APPS += ('debug_toolbar', )
INTERNAL_IPS = ('127.0.0.1',)
MIDDLEWARE_CLASSES += \
            ('debug_toolbar.middleware.DebugToolbarMiddleware', )

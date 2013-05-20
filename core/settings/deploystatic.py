# Django settings uploading static files to S3 using django-storages
# via collectstatic
import os
from .local import *

INSTALLED_APPS += ('storages',)

# Grab from environ (should be set in fabfile.py)
AWS_STORAGE_BUCKET_NAME = os.environ.get('AWS_STORAGE_BUCKET_NAME', '')

# Path within bucket
AWS_LOCATION = '{{ project_name }}'

STATICFILES_STORAGE = 'storages.backends.s3boto.S3BotoStorage'

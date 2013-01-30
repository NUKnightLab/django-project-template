README file for {{ project_name }}

**Important: keep secrets out of github. Use environment variables.**

===========
DEVELOPMENT
===========

Be sure to install the project requirements (preferably in a project-specific
virtual environment):

    ``pip install -r requirements.txt``

Run the development server:

    ``django-admin.py runserver --settings=core.settings.local``

Alternatively, indicate the settings with the DJANGO_SETTINGS_MODULE
environment variable.

We have seen some cases of Django not finding the specified settings module
with this approach. The solution is to explicitly indicate the current
directory on your PYTHONPATH with a dot (.):

    ``export PYTHONPATH=$PYTHONPATH:.``

For user-specific settings, do not modify the local.py file. Rather, create
a <username>.py settings file that imports the local settings. It is
recommended that you push your user-specific settings into version control
along with everything else, **but should not include any secrets.**

==========
DEPLOYMENT
==========

Projects a generally deployed to the application user's home directory in:

``/home/apps/sites``

Deployment is by direct clone from git. The name of the git repository
will be the name of the directory in ``sites`` that is created by the
``git clone`` command.

-------------------------------
Required environment variables:
-------------------------------
DJANGO_SETTINGS_MODULE
DJANGO_SECRET_KEY
*** Specify additional environment variables here ***


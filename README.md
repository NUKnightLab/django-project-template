README file for {{ project_name }}

**Important: keep secrets out of github. Use environment variables.**

###USAGE

Create a new Django project using this template:

    django-admin.py startproject --template=https://github.com/NUKnightLab/django-project-template/archive/master.zip <project_name>

Delete this USAGE section after creating the project. The remainder of this
README is for the created project.


###REQUIREMENTS

[virtualenvwrapper](http://virtualenvwrapper.readthedocs.org/en/latest/install.html)


###DEVELOPMENT

    # Clone secrets and fablib repositories
    git clone git@github.com:NUKnightLab/secrets.git
    git clone git@github.com:NUKnightLab/fablib.git
    
    # Change into project directory
    cd <project_name>
    
    # Make virtual environment
    mkvirtualenv <project_name>
    
    # Activate virtual environment
    workon <project_name>
    
    # Install requirements
    pip install -r requirements.txt
    
    # Setup (if necessary)
    fab loc setup
    
    # Start the development server
    python manage.py runserver
    

For user-specific settings, do not modify the loc.py file. Rather, create a <username>.py settings file that imports the local settings. It is recommended that you push your user-specific settings into version control
along with everything else, **but should not include any secrets.**  To run the development server with your user-specific settings:

    python manage.py runserver --settings=core.settings.<your username>
   
    
###DEPLOYMENT

Projects are deployed to the application user's home directory in: ``/home/apps/sites``

Deployment is by direct clone from git. The name of the git repository will be the name of the directory in ``sites`` that is created by the ``git clone`` command.

    # Do this once before the intial deployment (replace `stg` with `prd` for production)
    fab stg setup
    
    # Do this to deploy (replace `stg` with `prd` for production)
    fab stg deploy


###REQUIRED ENVIRONMENT VARIABLES:

- DJANGO_SETTINGS_MODULE
- DJANGO_SECRET_KEY
- WORKON_HOME (set manually if not using mkvirtualenv)




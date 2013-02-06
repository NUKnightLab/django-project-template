"""Deployment management for KnightLab web application projects.

Add the pem file to your ssh agent:

    ssh-add <pemfile>

Execute remote commands by specifying apps user @ remote host:

    fab -H apps@<public-dns> <command>
"""
import os
from fabric.api import env, put, require, run
from fabric.context_managers import cd, prefix
from fabric.contrib.files import exists

PROJECT_NAME = '{{ project_name }}'

# EXISTING SYSTEM AND REPO RESOURCES
APP_USER = 'apps'
PYTHON = 'python2.7'
REPO_URL = 'git@github.com:Knight-News-Innovation-Lab/%s.git' % PROJECT_NAME
CONF_DIRNAME = 'conf' # should contain stg & prd directories
APACHE_CONF_NAME = 'apache' # inside conf/stg, conf/prd
SSH_DIRNAME = '.ssh'
USERS_HOME = '/home'

# DEPLOYMENT SETTINGS
SITES_DIRNAME = 'sites'
ENV_DIRNAME = 'env' # virtualenvs go here


def _path(*args):
    return os.path.join(*args)


env.project_name = PROJECT_NAME
env.repo_url = REPO_URL
env.home_path = _path(USERS_HOME, APP_USER)
env.ssh_path = _path(env.home_path, SSH_DIRNAME)
env.sites_path = _path(env.home_path, SITES_DIRNAME)
env.project_path = _path(env.sites_path, env.project_name)
env.conf_path = _path(env.project_path, CONF_DIRNAME)
env.env_path = _path(env.home_path, ENV_DIRNAME)
env.ve_path = _path(env.env_path, env.project_name)
env.activate_path = _path(env.ve_path, 'bin', 'activate')
env.apache_path = _path(env.home_path, 'apache')
env.python = PYTHON


def _setup_ssh():
    with cd(env.ssh_path):
        # TODO: get these files from S3
        if not exists('known_hosts'):
            put('known_hosts', env.ssh_path) # TODO: can we cat this?
        if not exists('config'):
            put('config', env.ssh_path)
        if not exists('github.key'):
            put('github.key', env.ssh_path) # TODO: make this easily replaceable
            with cd(env.ssh_path):
                run('chmod 0600 github.key')
     

def _setup_directories():
    run('mkdir -p %(sites_path)s' % env)
    run('mkdir -p %(ve_path)s' % env)


def _setup_virtualenv():
    """Create a virtualenvironment."""
    run('virtualenv -p %(python)s %(ve_path)s' % env)


def _clone_repo():
    """Clone the git repository."""
    # TODO:set global config for git username and email
    run('git clone %(repo_url)s %(project_path)s' % env)


def _run_in_ve(command):
    """Execute the command inside the virtualenv."""
    with prefix('. %s' % env.activate_path):
        run(command)


def _install_requirements():
    with cd(env.project_path):
        if exists('requirements.txt'):
            _run_in_ve('pip install -r requirements.txt')


def _symlink(existing, link):
    if not exists(link):
        run('ln -s %s %s' % (existing, link))


def _link_apache_conf():
    # TODO: provisioning should cat Include line to apache.conf
    apache_conf = _path(env.conf_path, env.settings, APACHE_CONF_NAME)
    if exists(apache_conf):
        run('mkdir -p %(apache_path)s' % env)
        link_path = _path(env.apache_path, env.project_name)
        _symlink(apache_conf, link_path)


# TODO: specify hosts automatically by environment

def production():
    """Work on production environment
    """
    env.settings = 'prd'


def staging():
    """Work on production environment
    """
    env.settings = 'stg'


def setup():
    """Setup new application deployment. Do this only once per project."""
    require('settings', provided_by=[production, staging])
    # TODO: support for branches? what is the workflow?
    #require('branch', provided_by=[stable, master, branch])
    _setup_ssh()
    _setup_directories()
    _setup_virtualenv()
    _clone_repo()
    _install_requirements()
    _link_apache_conf()


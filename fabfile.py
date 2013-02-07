"""Deployment management for KnightLab web application projects.

Add the pem file to your ssh agent:

    ssh-add <pemfile>

Set your AWS credentials in environment variables:
    AWS_ACCESS_KEY_ID
    AWS_SECRET_ACCESS_KEY

or in config files:
    /etc/boto.cfg, or
    ~/.boto

Note: Do not quote key strings in the config files.

For AWS (boto) config details, see:
    http://boto.readthedocs.org/en/latest/boto_config_tut.html#credentials

USAGE:

fab <env> <operation>

i.e.: fab [stg|prd] [setup|hosts]

This will execute the operation for all web servers for the given environment
(stg, or prd).

To execute commands for a specific host, specify apps user @ remote host:

    fab -H apps@<public-dns> <env> <operation>
"""
import os
import sys
import tempfile
import boto
from boto import ec2
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
AWS_CREDENTIALS_ERR_MSG = """
    Unable to connect to AWS. Check your credentials. boto attempts to
    find AWS credentials in environment variables AWS_ACCESS_KEY_ID
    and AWS_SECRET_ACCESS_KEY, or in config files: /etc/boto.cfg, or
    ~/.boto. Do not quote key strings in config files. For details, see:
    http://boto.readthedocs.org/en/latest/boto_config_tut.html#credentials
"""

_ec2_con = None
_s3_con = None

def _get_ec2_con():
    global _ec2_con
    if _ec2_con is None:
        try:
            _ec2_con = boto.connect_ec2()
        except boto.exception.NoAuthHandlerFound:
            print AWS_CREDENTIALS_ERR_MSG
            sys.exit(0)
    return _ec2_con


def _get_s3_con():
    global _s3_con
    if _s3_con is None:
        try:
            _s3_con = boto.connect_s3()
        except boto.exception.NoAuthHandlerFound:
            print AWS_CREDENTIALS_ERR_MSG
            sys.exit(0)
    return _s3_con
        

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
env.app_user = APP_USER

import StringIO

class MyStream(StringIO.StringIO):
    def __init__(self, s, name):
        self.name = name
        super(MyStream, self).__init__(s)
 
def _copy_from_s3(bucket_name, resource, dest_path):
    """Copy a resource from S3 to a remote file."""
    bucket = _get_s3_con().get_bucket(bucket_name)
    key = bucket.lookup(resource)
    f = tempfile.NamedTemporaryFile(delete=False)
    key.get_file(f)
    f.close()
    put(f.name, dest_path)
    os.unlink(f.name)


def _setup_ssh():
    with cd(env.ssh_path):
        if not exists('known_hosts'):
            # TODO: should we cat this?
            _copy_from_s3('knightlab.ops', 'deploy/ssh/known_hosts',
                os.path.join(env.ssh_path, 'known_hosts'))
        if not exists('config'):
            _copy_from_s3('knightlab.ops', 'deploy/ssh/config',
                os.path.join(env.ssh_path, 'config'))
        if not exists('github.key'):
            # TODO: make github.key easily replaceable
            _copy_from_s3('knightlab.ops', 'deploy/ssh/github.key',
                os.path.join(env.ssh_path, 'github.key'))
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


def _get_ec2_reservations():
    try:
        return _get_ec2_con().get_all_instances()
    except boto.exception.EC2ResponseError, e:
        print "\nReceived error from AWS. Are your credentials correct?"
        print "Note: do not quote keys in boto config files."
        print "\nError from Amazon was:\n"
        print e
        sys.exit(0)


def _lookup_ec2_instances():
    """Get the EC2 instances for this working environment and load them
    into env."""
    instances = []
    prefix = '%s-app' % env.settings # currently only supporting app
    for r in _get_ec2_reservations():
        for i in r.instances:
            if i.tags.get('Name', '').startswith(prefix):
                instances.append(i)
    env.instances = instances


def _setup_env(env_type):
    """Setup the working environment as appropriate for stg, prd."""
    env.settings = env_type
    _lookup_ec2_instances()
    if not env.hosts: # allow user to specify hosts
        env.hosts = ['%s@%s' % (env.app_user, i.public_dns_name) for i in
            env.instances]
    print env.hosts
    

def prd():
    """Work on production environment."""
    _setup_env('prd')


def stg():
    """Work on staging environment."""
    _setup_env('stg')


def setup():
    """Setup new application deployment. Run only once per project."""
    require('settings', provided_by=[prd, stg])
    # TODO: support for branches? what is the workflow?
    #require('branch', provided_by=[stable, master, branch])

    _setup_ssh()
    _setup_directories()
    _setup_virtualenv()
    _clone_repo()
    _install_requirements()
    _link_apache_conf()


def hosts():
    """List applicable hosts for the specified environment.
    Use this to determine which hosts will be affected by an
    environment-specific operation."""
    require('settings', provided_by=[prd, stg])
    for host in env.instances:
        print env.hosts

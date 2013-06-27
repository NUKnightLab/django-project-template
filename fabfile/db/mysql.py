"""
postgres/postgis 

seed data:
    <project>/data/db/postgis/seed/
    
sample data:
    <project>/data/db/postgis/sample/
    
See _psql_pipe_data() for acceptable formats and file-naming conventions.
"""
from fabric.api import env, settings, hide
from fabric.contrib.files import exists
from fabric.decorators import roles, runs_once
import os
from ..utils import notice, warn, abort, path, ls, do, confirm
from . import django_sync


def _mysql(postfix, prefix=''):
    c = ' mysql -h %(mysql_host)s -u %(mysql_user)s '
    if env.mysql_password:
        c += '-p"%(mysql_password)s" '
    return env.doit((prefix+c+postfix) % env)
    
    
def _mysql_pipe_data(f):
    """
    Pipe data from a file to the db.  Valid types of files:
    
    1.  Files created using mysqldump (full SQL statements)

    These are loaded by piping their contents directly to mysql.
    
        any_name_is_fine.sql[.gz|.gzip|.zip|.Z]   

    Files that do not follow these naming conventions are skipped.
    """    
    (other, ext) = os.path.splitext(f)
    ext = ext.lower()
    if ext.lower() in ('.gz', '.gzip', '.zip', '.Z'):
        cmd = 'gunzip -c'
        (other, ext) = os.path.splitext(other) 
        ext = ext.lower()  
    else:
        cmd = 'cat'
        
    if ext == '.sql':
        _mysql(env.mysql_name, prefix='%s %s |' % (cmd, f))
    else:
        warn('Skipping file, unknown format (%s)' % f)     


def setup_env(conf):
    """Setup the working environment as appropriate for loc, stg, prd."""  
    env.mysql_name = conf['NAME']
    env.mysql_user = conf['USER']
    env.mysql_password = conf['PASSWORD']
    env.mysql_host = conf['HOST']
    
 
@roles('app')
@runs_once    
def setup():
    """
    Create the project database and user.
           
    For now, just check to make sure they exist, because the creation of either
    requires a root user/password, and I'm not sure how that will work.
    """
    with hide('warnings'), settings(warn_only=True):
        result = _mysql('-e "SHOW DATABASES;" | grep "^%(mysql_name)s$"')
    if result.failed:
        abort('Error connecting to "%(mysql_name)s" as "%(mysql_user)s"' \
            ' on host %(mysql_host)s:' % env)
    else:
        notice('Connected to "%(mysql_name)s" as "%(mysql_user)s"' \
            ' on host %(mysql_host)s' % env)


@roles('app', 'work')
@runs_once
def sync():
    django_sync()


@roles('app', 'work')
@runs_once
def seed(sample='n'):
    """
    Seed the database.  Set sample=y to load sample data (default = n).
    This needs to be run once per database, but has to be run from the
    app or work server, because we need to pipe data to mysql.
    """
    d = path(env.data_path, 'db', 'mysql', 'seed')   
    if exists(d):
        files = ls(d)     
        for f in files:
            _psql_pipe_data(f)                    

    d = path(env.data_path, 'db', 'mysql', 'sample')
    if do(sample) and exists(d):
        files = ls(d)        
        for f in files:
            notice('Seeding from %s' % f)
            _mysql_pipe_data(f)
    

@roles('app', 'work')
@runs_once
def destroy():
    """Remove the database and user."""   
    warn('db.mysql.destroy() not implemented')
    
    


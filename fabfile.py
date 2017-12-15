import os

from fabric.api import *
from fabric.contrib.project import rsync_project
from fabric.contrib import console
from fabric import utils
from fabtools import postgres


RSYNC_EXCLUDE = (
    '.DS_Store',
    '.hg',
    '*.pyc',
    '*.example',
    '*.db',
    'media/',
    'local_settings.py',
    'fabfile.py',
    'bootstrap.py',
)

DB = {
    "staging": {
        "user": "tathros",
        "password": "tathros",
        "db": "photo364"
    },
    "production": {
        "user": "tathros",
        "password": "tathros",
        "db": "photo365"
    }
}

env.home = '/home/tathros/tathros'
env.project = 'photobasa'


def _setup_path():
    env.root = os.path.join(env.home, env.environment)
    env.code_root = os.path.join(env.root, env.project)
    env.virtualenv_root = '/home/tathros/tathros-venv'
    env.settings = '{project}.settings_{environment}'.format(**env)


def staging():
    """ use staging environment on remote host"""
    env.user = 'tathros'
    env.environment = 'staging'
    env.hosts = ['136.243.151.13']
    _setup_path()


def production():
    """ use production environment on remote host"""
    utils.abort('Production deployment not yet implemented.')


def bootstrap():
    """ initialize remote host environment (virtualenv, deploy, update) """
    require('root', provided_by=('staging', 'production'))
    run('mkdir -p %(root)s' % env)
    run('mkdir -p %s' % os.path.join(env.home, 'log'))
    create_virtualenv()
    deploy()
    update_requirements()


def create_virtualenv():
    """ setup virtualenv on remote host """
    require('virtualenv_root', provided_by=('staging', 'production'))
    args = '--clear --distribute'
    run('virtualenv -p /usr/bin/python3 {} {}'.format(args, env.virtualenv_root))
    activate_file_path = os.path.join(env.virtualenv_root, 'bin/activate')
    with open(activate_file_path, "a") as activate_file:
        activate_file.write('export DJANGO_SETTINGS_MODULE="photobase.settings_dev"')


def server_prepare():
    """ installing all necessary packages """
    apt_packages = ('libpq-dev', 'python3-dev',
                    'libssl-dev', 'lib32ncurses5-dev', 'python3',
                    'postgresql', 'postgis',)
    sudo('apt-get install %s' % " ".join(apt_packages))
    sudo('easy_install pip')
    """ db routines """
    db_env = DB[env.environment]
    if not postgres.user_exists(db_env["user"]):
        postgres.create_user(db_env["user"], db_env["password"],
            createdb=True, createrole=True)
    if not postgres.database_exists(db_env['db']):
        postgres.create_database(db_env['db'], owner=db_env["user"])


def migrate():
    """ run Django migrations """
    with cd(env.code_root):
        run('%s python3 manage.py makemigrations' % fetch_activate())
        run('%s python3 manage.py migrate' % fetch_activate())


def deploy():
    """ rsync code to remote host """
    with shell_env(root=env.home):
        require('root', provided_by=('staging', 'production'))
        if env.environment == 'production':
            if not console.confirm('Are you sure you want to deploy production?',
                                   default=False):
                utils.abort('Production deployment aborted.')
        extra_opts = '--omit-dir-times'
        rsync_project(
            env.root,
            exclude=RSYNC_EXCLUDE,
            delete=True,
            extra_opts=extra_opts,
        )
        #restart_wsgi()

def fetch_activate():
    activate_path = os.path.join(env.virtualenv_root, 'bin/activate')
    return 'source %s &&' % activate_path

def update_requirements():
    """ update external dependencies on remote host """
    with shell_env(root=env.home):
        require('root', provided_by=('staging', 'production'))
        requirements = os.path.join(env.code_root, 'requirements')
        with cd(env.code_root):
            cmd = ['%s pip install' % fetch_activate()]
            cmd += ['-r %s' % requirements]
            run(' '.join(cmd))


def restart_wsgi():
    """ reload wsgi on remote host via service"""
    with shell_env(root=env.home):
        require('root', provided_by=('staging', 'production'))
        # run('systemctl restart tathros.service')
        run("ps aux |grep gunicorn |grep tathros | awk '{ print $2 }' |xargs kill -HUP")


def reset_local_media():
    """ Reset local media from remote host """
    require('root', provided_by=('staging', 'production'))
    media = os.path.join(env.code_root, 'media', 'upload')
    local('rsync -rvaz {}@{}:{} media/'.format(env.user, env.hosts[0], media))

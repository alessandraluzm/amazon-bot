import time

from fabric.contrib.files import exists
from fabric.operations import require, local, sudo, run, put
from fabric.state import env

from conf.production.server import machine as production


env.project_name = 'amazonbot'
env.python_version = '3.5'
""" Python version used to install on the system and for the virtual env. """

servers = [production]


# noinspection SpellCheckingInspection
def setup():
    """ Setup the machine to receive the first server instance and deploy. """
    require('hosts', provided_by=servers)
    require('path')
    packages_to_install = ['python' + env.python_version, 'python-pip']
    for package in packages_to_install:
        sudo('apt-get install -y ' + package)
    sudo('pip install virtualenv')
    run('mkdir -p %(path)s; cd %(path)s; virtualenv env --python=python%(python_version)s;' % env)
    run('cd %(path)s; mkdir releases; mkdir packages; mkdir logs; mkdir static; mkdir media; chmod -R 777 media;' % env)
    deploy()


def deploy():
    """ Deploy the latest version of the site to the servers. """
    require('hosts', provided_by=servers)
    require('path')
    env.release = time.strftime('%Y-%m-%d-%H-%M')
    upload_tar_from_git()
    install_requirements()
    symlink_current_release()


def upload_tar_from_git():
    """ Create an archive from git and upload it. """
    require('release', provided_by=[deploy, setup])
    local('git archive --format=tar %(git_branch)s | gzip > %(release)s.tar.gz' % env)
    run('mkdir %(path)s/releases/%(release)s' % env)
    put('%(release)s.tar.gz' % env, '%(path)s/packages/' % env)
    run('cd %(path)s/releases/%(release)s && tar zxf ../../packages/%(release)s.tar.gz' % env)
    local('rm %(release)s.tar.gz' % env)
    run('rm %(path)s/packages/%(release)s.tar.gz' % env)


def install_requirements():
    """ Use pip to install the requirements. """
    require('release', provided_by=[deploy, setup])
    run('source %(path)s/env/bin/activate; cd %(path)s; pip install -r ./releases/%(release)s/conf/requirements.txt' % env)


def symlink_current_release():
    """ Replace the current version with the latest upload. """
    require('release', provided_by=[deploy, setup])
    if exists('%(path)s/releases/previous' % env):
        run('rm %(path)s/releases/previous' % env)
    if exists('%(path)s/releases/current' % env):
        run('mv %(path)s/releases/current %(path)s/releases/previous' % env)
    run('ln -s %(path)s/releases/%(release)s/ %(path)s/releases/current' % env)
    if exists('conf/%(config_dir)s/local.py' % env):
        put('conf/%(config_dir)s/local.py' % env, '%(path)s/releases/current/%(project_name)s/' % env)


def rollback():
    """
    Roll back to the previously current version of the code.

    Rolling back again will swap between the two latest versions.
    """
    require('hosts', provided_by=servers)
    require('path')
    run('cd %(path)s; mv releases/current releases/_previous;' % env)
    run('cd %(path)s; mv releases/previous releases/current;' % env)
    run('cd %(path)s; mv releases/_previous releases/previous;' % env)

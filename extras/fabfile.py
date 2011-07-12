# -*- coding: utf-8 -*-
"""
    Fabfile

    A Fabric deployment script to install Sphinx Search and the Sphinx Search's
    on a Ubuntu >= 10.04 machine.

    :copyright: (c) 2011 by Douglas Morato
    :license: BSD, see LICENSE for more details.
"""
from fabric.api import run, cd, sudo


def _install_sphinx_dependencies():
    """Sphinx depends on build-essentials and Postgres header.

    This script also install posgresql-server-dev-9.0 header to enable support
    for Postgres databases on Sphinx Search
    """
    sudo('apt-get install -y python-software-properties')
    sudo('apt-add-repository ppa:pitti/postgresql')
    sudo('apt-get update')
    sudo('apt-get install -y postgresql-server-dev-9.0')
    sudo('apt-get install -y build-essential')

def install_sphinx_search():
    """Download and compile Sphinx Search from source code,with libstemmer,
    PostgreSQL and 64-bit integer support.
    """
    _install_sphinx_dependencies()
    with cd('/tmp'):
        #Download and uncompress sphinx search server
        run('wget http://sphinxsearch.com/files/sphinx-2.0.1-beta.tar.gz')
        run('tar -xvzf sphinx-2.0.1-beta.tar.gz')

        # download and uncompress libstemmer we can enable more languagues
        # the stemming process
        run('wget http://snowball.tartarus.org/dist/libstemmer_c.tgz')
        run('tar -xvzf libstemmer_c.tgz')

        # copy libstemmer to sphinx build dist so sphinx can be build with
        # libstemmer support
        run('cp -fa libstemmer_c/* sphinx-2.0.1-beta/libstemmer_c/')

    # Configure Sphinx to be buil to our enviroment
    with cd('/tmp/sphinx-2.0.1-beta'):
        run('./configure --prefix=/etc/sphinx --without-mysql --with-pgsql' \
            ' --enable-id64 --with-libstemmer')
        # Build sphinx from source
        sudo('make -j4 install')

    # Make symbolic links of the sphinx tools so we don't need to add them
    # user or to system path
    with cd('/usr/local/bin'):
        sudo('ln -s /etc/sphinx/bin/indexer')
        sudo('ln -s /etc/sphinx/bin/indextool')
        sudo('ln -s /etc/sphinx/bin/search')
        sudo('ln -s /etc/sphinx/bin/searchd')
        sudo('ln -s /etc/sphinx/bin/spelldump')

    # Create log directory
    sudo('mkdir /var/log/sphinx')

def install_tryton_sphinx():
    run("pip install -e git+git://github.com/dfamorato/tryton_search.git")

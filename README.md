A Tryton ERP module to enable Sphinx Search Server integration

This is a work in progress, more information can be found at:
http://trytonsearch.blogspot.com

**THIS IS A WORK IN PROGRESS.**

## Installation of the Sphinx Search Server - THE EASY WAY
**If you have an Ubuntu Server >= 10.04 , YOU ARE LUCKY:**

### ASSUMPTIONS
* I assume that have a clean Ubuntu machine version >= 10.04
* I assume that you want to use PostgreSQL 9 as you Database
* I assume that you don't have postgres install
* I assume that you already have Tryton installed
* I assume that you sudo (or root) access on the target machine
* I will install PostgreSQL from a ppa
* I will use `python fabric` to make the installation
* I assume that you have backed up you data

**If you understood the assumptions, then you can proceed:**

It is highly recommended that you do the following in a `virtualenv` so that your root python environment is not F**ked! 

Install virtualenv:

    easy_install virtualenv

To create a virtualenv:

    virtualenv tryton_search

**Installing Sphinx:**

If you want to use the bundled helper to install sphinx server

    pip install fabric
    wget https://raw.github.com/dfamorato/tryton_sphinx/master/extras/fabfile.py 
    fab -u `username` -H `target_machine` install_sphinx_search

**Installing the module**

    git clone git://github.com/dfamorato/tryton_sphinx.git
    cd tryton_sphinx
    python setup.py install

## Installation requirements

* TrytonSphinx module requires you to have either a `PostgreSQL` or a `MySQL` database.
* You will need the `build-essentials` package in order to compile Sphinx Search Server
from the source code.


## TODO:

### Installation of the Sphinx Search Server - THE HARD WAY

    DOCUMENTATION TO BE DONE
    
### Building Sphinx Search Config File  

The module installs a script to your environments bin called `tryton-sphinx-buildconf` which could be used to build the sphinx config from your tryton database and configuration file.

    tryton-sphinx-buildconf.py --help

    Usage: tryton-sphinx-buildconf.py [options] database filename

    Options:
      -h, --help            show this help message and exit
      -c CONFIG, --config=CONFIG
                        The tryton configuration file to use

an example usage of the file would be:

    tryton-sphinx-buildconf.py -c /etc/trytond.conf database_name sphinx.conf

and the script will iterate through all your models and generate the corresponding sphinx config file.

### Building Sphinx Search Index
    
To build the index, use the sphinx.conf file generated in the previous step with the indexer program that was installed by sphinx. Example:

    indexer -c sphinx.conf --all

This creates all indexes. The second time you run the indexer, the files need to be rotated and hence pass `--rotate` argument in addition.

The index files are created in a directory called `sphinx`in the data path specified in the tryton config. Ensure that the same exists.

### Starting the search server

`searchd`is the search daemon

    searchd -c sphinx.conf

### Examples on how to query the search index

sphinx comes bundled with a client to `searchd` and is available as a program called `search`. This could be used to test the search without writing any API code at all. For example to search inside the product index for a product name say 'iphone' you could write:

    search -c sphinx.conf -i product_template iphone

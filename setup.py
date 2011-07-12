# -*- coding: utf-8 -*-
"""
    setup

    Setup the tryton_sphinx module.

    TODO: Write a description

    :copyright: (c) 2011 by Douglas Morato
    :license: BSD, see LICENSE for more details.
"""
from setuptools import setup

__author__ = 'Douglas Morato'
__version__ = '0.1'

setup(
    name = "TrytonSphinx",
    version = __version__,

    packages = [
        'tryton_sphinx'
        ],
    package_dir = {
        'tryton_sphinx': 'api',
        },
    scripts = ['bin/tryton-sphinx-buildconf.py'],

    install_requires = [
        'trytond>=2.0',
        'distribute',
        'jinja2',
        ],


    # metadata for upload to PyPI
    author = __author__,
    author_email = "dfamorato@gmail.com",
    description = __doc__,
    license = "BSD",
    keywords = "tryton sphinx search",
    url = "http://douglasmorato.com",   # project home page, if any

    # TODO: also include long_description, download_url, classifiers, etc.
)


# -*- coding: utf-8 -*-
"""
    setup

    Setup the tryton_sphinx module.

    TODO: Write a description

    :copyright: (c) 2011 by Douglas Morato
    :license: BSD, see LICENSE for more details.
"""
from setuptools import setup
import re

__author__ = 'Douglas Morato'
__version__ = '0.2'

requires = [
    'distribute',
    'jinja2',
    ]
packages = [
    'tryton_sphinx',
    'trytond.modules.search',
    ]
package_dir = {
    'tryton_sphinx': 'api',
    'trytond.modules.search': 'module',
    }

trytond_module_info = eval(open('module/__tryton__.py').read())
major_version, minor_version, _ = trytond_module_info.get(
    'version', '0.0.1').split('.', 2)
major_version = int(major_version)
minor_version = int(minor_version)

for dep in trytond_module_info.get('depends', []):
    if not re.match(r'(ir|res|workflow|webdav)(\W|$)', dep):
        requires.append('trytond_%s >= %s.%s, < %s.%s' %
                (dep, major_version, minor_version, major_version,
                    minor_version + 1))
requires.append('trytond >= %s.%s, < %s.%s' %
        (major_version, minor_version, major_version, minor_version + 1))

package_data = {
    'trytond.modules.search': trytond_module_info.get('xml', []) \
            + trytond_module_info.get('translation', []),
    }
entry_points = """
[trytond.modules]
search = trytond.modules.search
"""

setup(
    name = "TrytonSphinx",
    version = __version__,

    packages = packages,
    package_dir = package_dir,
    package_data = package_data,
    scripts = ['bin/tryton-sphinx-buildconf.py'],

    install_requires = requires,
    entry_points=entry_points,

    # metadata for upload to PyPI
    author = __author__,
    author_email = "dfamorato@gmail.com",
    description = __doc__,
    license = "BSD",
    keywords = "tryton sphinx search",
    url = "http://douglasmorato.com",   # project home page, if any

    # TODO: also include long_description, download_url, classifiers, etc.
)


#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# haggis: a library of general purpose utilities
#
# Copyright (C) 2019  Joseph R. Fox-Rabinovitz <jfoxrabinovitz at gmail dot com>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

# Author: Joseph Fox-Rabinovitz <jfoxrabinovitz at gmail dot com>
# Version: 13 Apr 2019: Initial Coding


"""
Setup script for building and installing haggis.
"""

from os.path import dirname, join
import sys

from setuptools import setup


DIST_NAME = 'haggis'

LICENSE = 'GNU Affero General Public License v3 or later (AGPLv3+)'
DESCRIPTION = 'General purpose utility library'

AUTHOR = 'Joseph R. Fox-Rabinovitz'
AUTHOR_EMAIL = 'jfoxrabinovitz@gmail.com'

MAINTAINER = 'Joseph R. Fox-Rabinovitz'
MAINTAINER_EMAIL = 'jfoxrabinovitz@gmail.com'

CLASSIFIERS = [
    'Development Status :: 2 - Pre-Alpha',
    'Intended Audience :: Developers',
    'Intended Audience :: Other Audience',
    'License :: OSI Approved :: GNU Affero General Public License v3 or later (AGPLv3+)',
    'Operating System :: Microsoft :: Windows',
    'Operating System :: POSIX :: Linux',
    'Operating System :: Unix',
    'Programming Language :: Python',
    'Programming Language :: Python :: 3 :: Only',
    'Programming Language :: Python :: 3.6',
    'Programming Language :: Python :: 3.7',
    'Programming Language :: Python :: 3.8',
    'Programming Language :: Python :: 3.9',
    'Programming Language :: Python :: 3.10',
    'Topic :: Software Development :: Libraries',
    'Topic :: System :: Console Fonts',
    'Topic :: System :: Logging',
    'Topic :: Terminals',
    'Topic :: Text Processing',
    'Topic :: Text Processing :: General',
    'Topic :: Text Processing :: Markup',
    'Topic :: Text Processing :: Markup :: LaTeX',
    'Topic :: Text Processing :: Markup :: XML',
    'Topic :: Utilities',
]


COMMANDS = {}


try:
    from sphinx.setup_command import BuildDoc
    COMMANDS['build_sphinx'] = BuildDoc
except ImportError:
    pass


def import_file(name, location):
    """
    Imports the specified python file as a module, without explicitly
    registering it to `sys.modules`.

    While haggis uses Python 3 features, you are free to try to install
    it in a Python 2 environment.
    """
    if sys.version_info[0] == 2:
        # Python 2.7-
        from imp import load_source
        mod = load_source(name, location)
    elif sys.version_info < (3, 5, 0):
        # Python 3.4-
        from importlib.machinery import SourceFileLoader
        mod = SourceFileLoader(name, location).load_module()
    else:
        # Python 3.5+
        from importlib.util import spec_from_file_location, module_from_spec
        spec = spec_from_file_location(name, location)
        mod = module_from_spec(spec)
        spec.loader.exec_module(mod)
    return mod


def version_info():
    """
    Jump through some hoops to import version.py for the different
    versions of Python.

    https://stackoverflow.com/a/67692/2988730
    """
    location = join(dirname(__file__) or '.', 'src', 'haggis', 'version.py')
    mod = import_file('version', location)
    return mod.__version__


def long_description():
    """
    Reads in the README and CHANGELOG files, separated by two
    newlines.
    """
    with open('README.md') as readme, open('CHANGELOG') as changes:
        return '%s\n\n%s' % (readme.read(), changes.read())


if __name__ == '__main__':
    setup(
        name=DIST_NAME,
        version=version_info(),
        license=LICENSE,
        description=DESCRIPTION,
        long_description_content_type='text/markdown',
        long_description=long_description(),
        author=AUTHOR,
        author_email=AUTHOR_EMAIL,
        maintainer=MAINTAINER,
        maintainer_email=MAINTAINER_EMAIL,
        classifiers=CLASSIFIERS,
        url='https://github.com/madphysicist/haggis',
        project_urls={
            'Bugs': 'https://github.com/madphysicist/haggis/issues',
            'Documentation': 'https://haggis.readthedocs.io/en/stable/',
        },
        packages=[
            'haggis',
            'haggis.files',
            'haggis.tests',
            'haggis.files.tests',
        ],
        package_dir={'': 'src'},
        package_data={'haggis.files': ['_resources/*.XSL'],
                      'haggis.tests': ['data/*']},
        install_requires=['numpy >= 1.10'],
        extras_require={
            'all': [
                'astropy >= 3.0',
                'colorama >= 0.3;platform_system=="Windows"',
                'matplotlib >= 1.5',
                'openpyxl >= 2.4.8',
                'python-docx >= 0.8.5',
                'scipy > 0.16',
            ],
            'docx': ['python-docx >= 0.8.5'],
            'latex': [],
            'pdf': [],
            'ps': [],
            'plot': ['matplotlib >= 1.5'],
            'scio': ['scipy > 0.16', 'astropy >= 3.0'],
            'term': ['colorama >= 0.3;platform_system=="Windows"'],
            'xlsx': ['openpyxl >= 2.4.8'],
        },
        provides=['haggis'],
        tests_require=['pytest'],
        data_files = [('', ['LICENSE', 'README.md', 'CHANGELOG'])],
        cmdclass=COMMANDS,
    )

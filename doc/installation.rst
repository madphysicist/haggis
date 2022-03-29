.. haggis: a program for creating documents from data and content templates

.. Copyright (C) 2019  Joseph R. Fox-Rabinovitz <jfoxrabinovitz at gmail dot com>

.. This program is free software: you can redistribute it and/or modify
.. it under the terms of the GNU Affero General Public License as
.. published by the Free Software Foundation, either version 3 of the
.. License, or (at your option) any later version.

.. This program is distributed in the hope that it will be useful,
.. but WITHOUT ANY WARRANTY; without even the implied warranty of
.. MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
.. GNU Affero General Public License for more details.

.. You should have received a copy of the GNU Affero General Public License
.. along with this program. If not, see <https://www.gnu.org/licenses/>.

.. Author: Joseph Fox-Rabinovitz <jfoxrabinovitz at gmail dot com>
.. Version: 13 Apr 2019: Initial Coding


.. _installation:

==================
Installation Guide
==================

This document explains how to install Haggis.


.. _installation-install:

----------------------
Installing the Package
----------------------


.. _installation-pypi:

PyPI
====

Haggis is available via `pypi`_, so the recommended way to install it is ::

    pip install haggis

This performs a bare-bones install that depends only on the `numpy`_ library.
Some of the modules in the libary will not be active without extras. To install
all available extras, do ::

    pip install haggis[all]


.. _installation-extras:

Extras
======

To avoid unnecessary heavy dependencies, some of the features of Haggis are only
enabled if extras are installed. To install an extra, specify the name, or a
comma-separated list of names, in square brackets, e.g.::

    pip install haggis[plot,scio]

The following extras are supported:

+---------------+-------------------------+--------------------------+
| Extra         | Dependencies            | Affected Modules         |
+===============+=========================+==========================+
| all           | All shown below         | All shown below          |
+---------------+-------------------------+--------------------------+
| docx          | `python-docx`_ >= 0.8.5 | :mod:`haggis.files.docx` |
+---------------+-------------------------+--------------------------+
|               | `LaTeX`_                |                          |
| latex         | `dvips`_                | :mod:`haggis.latex_util` |
|               | `ImageMagick`_          |                          |
+---------------+-------------------------+--------------------------+
| pdf           | `Poppler`_              | :mod:`haggis.files.pdf`  |
|               | `ImageMagick`_          |                          |
+---------------+-------------------------+--------------------------+
| ps            | `GhostScript`_          | :mod:`haggis.files.ps`   |
+---------------+-------------------------+--------------------------+
| plot          | `matplotlib`_ >= 1.5    | :mod:`haggis.mpl_util`   |
|               |                         | :mod:`haggis.latex_util` |
+---------------+-------------------------+--------------------------+
| scio          | `astropy`_ >= 3.0       | :mod:`haggis.files.fits` |
|               | `scipy`_ >= 0.16        |                          |
+---------------+-------------------------+--------------------------+
| term          | `colorama`_ >= 0.3      |                          |
|               | [Windows only]          |                          |
+---------------+-------------------------+--------------------------+
| xlsx          | `openpyxl`_ >= 2.4.8    | :mod:`haggis.files.xlsx` |
+---------------+-------------------------+--------------------------+

Python dependencies are installed automatically by :program:`pip` when the
corresponding extra is selected. External dependencies are not.


.. _installation-source:

Source
======

Haggis uses `setuptools`_, so you can install it from source as well. If you
have a copy of the source distribution, run ::

    python setup.py install

from the project root directory, with the appropriate privileges. A source
distribution can be found on `PyPI`_ as well as directly on `GitHub`_.

You can do the same thing with :program:`pip` if you prefer. Any of the
following should work, depending on how you obtained your distribution ::

    pip install git+<URL>/haggis.git@master[all]  # For a remote git repository
    pip install haggis.zip[all]                   # For an archived file
    pip install haggis[all]                       # For an unpacked folder or repo

Using :program:`setup.py` or :program:`pip` should take care of all the Python
dependencies.


.. _installation-tests:

-----
Tests
-----

Haggis does not currently have any formal unit tests worth mentioning.
Eventually, pytest-compatible tests will be added in the
:py:mod:`~haggis.tests` package.


.. _installation-documentation:

-------------
Documentation
-------------

This documentation is built with `sphinx`_ (version >= 1.7.1 required).

The API documentation requires the `napoleon`_ extension, which is now bundled
with sphinx itself. The default viewing experience for the documentation is
provided by the `ReadTheDocs Theme`_, which is, however, optional. A version
>= 0.4.0 is recommended, but not required.

The documentation can be built from the complete source distribution by using
the specially defined command::

    python setup.py build_sphinx

Alternatively (perhaps preferably), it can be built using the provided
Makefile::

    cd doc
    make html

Both options work on Windows and Unix-like systems that have :program:`make`
installed. The Windows version does not require :program:`make`. On Linux you
can also do ::

    make -C doc html

The documentation can be found directly on `GitHub`_, or in the source
distribution on `PyPI`_. It is not avialable in binary distributions.
Any optional Python dependencies that are missing will affect how the
documentation is built. Module attributes that are disabled on the local
system will not be documented.


.. include:: /link-defs.rst

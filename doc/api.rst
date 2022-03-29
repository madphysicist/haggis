.. haggis: a library of general purpose utilities

.. Copyright (C) 2019  Joseph R. Fox-Rabinovitz <jfoxrabinovitz at gmail dot com>

.. This program is free software: you can redistribute it and/or modify
.. it under the terms of the GNU Affero General Public License as
.. published by the Free Software Foundation, either version 3 of the
.. License, or (at your option) any later version.

.. This program is distributed in the hope that it will be useful,
.. but WITHOUT ANY WARRANTY; without even the implied warranty of
.. MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
.. GNU Affero General Public License for more details.

.. You should have received a copy of the GNU Affero General Public License
.. along with this program. If not, see <https://www.gnu.org/licenses/>.

.. Author: Joseph Fox-Rabinovitz <jfoxrabinovitz at gmail dot com>
.. Version: 13 Apr 2019: Initial Coding


.. _api:

========
API Docs
========

.. _api-contents:

--------------------
Modules and Packages
--------------------

.. autosummary::

   haggis
   haggis.configuration
   haggis.ctypes_util
   haggis.exceptions
   haggis.files
   haggis.files.csv
   haggis.files.docx
   haggis.files.fits
   haggis.files.pdf
   haggis.files.ps
   haggis.files.ui
   haggis.files.xlsx
   haggis.files.xml
   haggis.files.zip
   haggis.latex_util
   haggis.load
   haggis.logs
   haggis.mapping
   haggis.math
   haggis.mpl_util
   haggis.npy_util
   haggis.numbers
   haggis.objects
   haggis.os
   haggis.recipes
   haggis.string_util
   haggis.structures
   haggis.threads
   haggis.time


-----------------------
``haggis`` root package
-----------------------

.. automodule:: haggis
   :members:

   ----------
   Attributes
   ----------

   .. attribute:: __version__

      The current version is |release|.


------------------------
``configuration`` module
------------------------

.. automodule:: haggis.configuration
   :members:


----------------------
``ctypes_util`` module
----------------------

.. automodule:: haggis.ctypes_util
   :members:


---------------------
``exceptions`` module
---------------------

.. automodule:: haggis.exceptions
   :members:


-----------------
``files`` package
-----------------

.. automodule:: haggis.files
   :members:
   :special-members: __enter__, __exit__, __repr__, __getitem__, __iter__


--------------------
``files.csv`` module
--------------------

.. automodule:: haggis.files.csv
   :members:


---------------------
``files.docx`` module
---------------------

.. automodule:: haggis.files.docx
   :members:


---------------------
``files.fits`` module
---------------------

.. automodule:: haggis.files.fits
   :members:


--------------------
``files.pdf`` module
--------------------

.. automodule:: haggis.files.pdf
   :members:


-------------------
``files.ps`` module
-------------------

.. automodule:: haggis.files.ps
   :members:


-------------------
``files.ui`` module
-------------------

.. automodule:: haggis.files.ui
   :members:


---------------------
``files.xlsx`` module
---------------------

.. automodule:: haggis.files.xlsx
   :members:


--------------------
``files.xml`` module
--------------------

.. automodule:: haggis.files.xml
   :members:


--------------------
``files.zip`` module
--------------------

.. automodule:: haggis.files.zip
   :members:


---------------------
``latex_util`` module
---------------------

.. automodule:: haggis.latex_util
   :members:


---------------
``load`` module
---------------

.. automodule:: haggis.load
   :members:


---------------
``logs`` module
---------------

.. automodule:: haggis.logs
   :members:


------------------
``mapping`` module
------------------

.. automodule:: haggis.mapping
   :members:
   :special-members: __init__, __getitem__


---------------
``math`` module
---------------

.. automodule:: haggis.math
   :members:


-------------------
``mpl_util`` module
-------------------

.. automodule:: haggis.mpl_util
   :members:


-------------------
``npy_util`` module
-------------------

.. automodule:: haggis.npy_util
   :members:


------------------
``numbers`` module
------------------

.. automodule:: haggis.numbers
   :members:


------------------
``objects`` module
------------------

.. automodule:: haggis.objects
   :members:


-------------
``os`` module
-------------

.. automodule:: haggis.os
   :members:


------------------
``recipes`` module
------------------

.. automodule:: haggis.recipes
   :members:
   :special-members: __init__, __getitem__, __enter__, __exit__


----------------------
``string_util`` module
----------------------

.. automodule:: haggis.string_util
   :members:


---------------------
``structures`` module
---------------------

.. automodule:: haggis.structures
   :members:
   :special-members: __init__, __contains__, __len__, __iter__,
                     __repr__, __str__


------------------
``threads`` module
------------------

.. automodule:: haggis.threads
   :members:
   :special-members: __init__


---------------
``time`` module
---------------

.. automodule:: haggis.time
   :members:
   :special-members: __init__, __enter__, __exit__, __str__

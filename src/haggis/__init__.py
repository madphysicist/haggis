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
The root package of the haggis library. The packages in this library are
arranged mostly by category. Some of the dependencies to the various
types of utilities are optional, and the corresponding modules will only
work fully if the dependencies are present.
"""

__all__ = ['__version__', 'Sentinel',]


#: The current version of the software
from .version import __version__


class _Sentinel:
    """
    A class that can be used to create sentinel objects for cases where
    :py:obj:`None` is not suitable for some reason.

    This class's truth value is always :py:obj:`False`. It does not
    allow any additional attributes to be added.
    """
    __slots__ = ()

    def __bool__(self):
        """
        Ensure that instances are always falsy.
        """
        return False


#: A sentinel object that can be used when :py:obj:`None` is not a
#: suitable option (e.g., when :py:obj:`None` has a special meaning).
#:
#: This object evaluates to boolean :py:obj:`False`.
Sentinel = _Sentinel()

del _Sentinel


def _display_missing_extra(extra, libs=None):
    """
    Print a message to standard error regarding a missing extra.
    """
    from sys import stderr
    print(
        'This feature is only enabled with the [{extra}] extra. Try\n\n'
        'pip install haggis[{extra}]'.format(extra=extra), file=stderr
    )
    if libs:
        if isinstance(libs, str):
            libs = [libs]
        print(
            '\nor install {} '
            'manually'.format(', '.join(str(lib) for lib in libs)), file=stderr
        )

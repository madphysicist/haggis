# -*- coding: utf-8 -*-

# haggis: a library of general purpose utilities
#
# Copyright (C) 2022  Joseph R. Fox-Rabinovitz <jfoxrabinovitz at gmail dot com>
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
# Version: 20 Jan 2022: Initial Coding


"""
Tests for the :py:mod:`haggis.objects` module.
"""

from array import array
import sys

import numpy

from ..objects import getsizeof


class TestGetsizeof:
    def setup(self):
        """
        Find the size of 'a', 'b', 1, 2 combined.
        """
        self.size = (
             sys.getsizeof('a') + sys.getsizeof(1) +
             sys.getsizeof('b') + sys.getsizeof(2)
        )

    def test_simple(self):
        """
        Show that simple objects have system size.
        """
        for obj in 32, None:
            assert getsizeof(obj) == sys.getsizeof(obj)

    def test_mapping(self):
        """
        Show that mappings are the sum of their components.
        """
        obj = {'a': 1, 'b': 2}
        assert getsizeof(obj) == sys.getsizeof(obj) + self.size

    def test_iterable(self):
        """
        Show that iterables are the sum of their components.
        """
        base = {'a', 1, 'b', 2}
        for c in list, set, frozenset, tuple:
            obj = c(base)
            assert getsizeof(obj) == sys.getsizeof(obj) + self.size

    def test_array(self):
        """
        Show that all array/string types have system size.
        """
        obj = b'test'
        assert getsizeof(obj) == sys.getsizeof(obj)
        obj = bytearray(obj)
        assert getsizeof(obj) == sys.getsizeof(obj)
        obj = array('b', obj)
        assert getsizeof(obj) == sys.getsizeof(obj)
        obj = str(obj)
        assert getsizeof(obj) == sys.getsizeof(obj)
        obj = numpy.array(list(obj))
        assert getsizeof(obj) == sys.getsizeof(obj)

    def test_loop(self):
        """
        Show that loops are handled correctly.
        """
        obj = {'a': 1, 'b': 2, 'c': None}
        obj['c'] = obj
        assert getsizeof(obj) == sys.getsizeof(obj) + self.size + \
                                 sys.getsizeof('c')

    def test_duplicate(self):
        """
        Show that duplicates are handled correctly.
        """
        obj = 10 * ['a', 1, 'b', 2]
        assert getsizeof(obj) == sys.getsizeof(obj) + self.size

    def test_nested(self):
        """
        Shows mixed types with nesting.
        """
        obj = {'a': 1, 'b': [], 'c': ({'d', 'e'}, {'f': 6})}
        size = (sys.getsizeof(obj) +
            sys.getsizeof('a') + sys.getsizeof(1) +
            sys.getsizeof('b') + sys.getsizeof(obj['b']) +
            sys.getsizeof('c') + sys.getsizeof(obj['c']) +
                                 sys.getsizeof(obj['c'][0]) +
                                     sys.getsizeof('d') + sys.getsizeof('e') +
                                 sys.getsizeof(obj['c'][1]) +
                                     sys.getsizeof('f') + sys.getsizeof(6)
        )
        assert getsizeof(obj) == size

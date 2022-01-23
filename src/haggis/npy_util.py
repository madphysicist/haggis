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
# Version: 22 Jan 2022: Initial Coding


"""
Utilities for manipulating non-computational aspects of numpy arrays.

Mathematical computations belong in :py:mod:`haggis.math`.
"""

from math import ceil, log

import numpy

from . import Sentinel
from .numbers import digit_count


__all__ = ['isolate_dtype', 'map_array']


def isolate_dtype(dtype, char='O'):
    """
    Create a new dtype that only contains the fields and subfields
    of `dtype` matching primitive type given by letter `char`.

    The new dtype will be flat with N fields containing the
    offsets to the original elements of interest. It will have the
    same `itemsize` as `dtype`. Field names are not preserved.

    Parameters
    ----------
    dtype : numpy.dtype
        Data type to parse out
    char : str[1]
        Primitive type character code to search for

    Return
    ------
    isolated : dtype
        A dtype containing offsets to all instances of `char` in
        `dtype`.
    """
    def dfs(dtype, base):
        """
        A DFS search will be more likely to yield offsets in the
        correct order without sorting.

        Parameters
        ----------
        dtype :
            The root of the current branch.
        base :
            The offset of dtype within its parent.

        Return
        ------
        offsets :
            The list of offsets of matching primitive fields found
            so far.
        """
        # Structure
        if dtype.fields is not None:
            offsets = []
            for dt, offset in dtype.fields.values():
                offsets.extend(dfs(dt, base + offset))
            return offsets
        # Array
        elif dtype.subdtype is not None:
            offsets = dfs(dtype.subdtype[0], base)
            return list(
                (offsets + dtype.subdtype[0].itemsize *
                 numpy.arange(numpy.prod(dtype.shape))[:, None]).ravel()
            )
        # Primitive
        elif dtype.char == char:
            return [base]
        return []

    offsets = dfs(dtype, 0)
    n = len(offsets)
    k = digit_count(n)
    # Generate names
    names = [f'a{i + 1:0{k}d}' for i in range(n)]
    d = {'names': names, 'offsets': offsets,
         'formats': n * [char], 'itemsize': dtype.itemsize}
    return numpy.dtype(d)


def map_array(map, arr, value=None, default=Sentinel):
    """
    Convert the elements of a numpy array using a mapping.

    The implementation uses looping to interface between the python and
    numpy datasets, but is as efficient as possible under the
    circumstaces. Intended for mapping a small number of arbitrary
    labels to some alternative value.

    Parameters
    ----------
    map : Mapping
        The mapping to apply. Any object with a `get` method that
        supports default values is accepted.
    arr : array-like
        The array to convert.
    value : callable, optional
        A function to apply to the dictionary values before placing in
        the output array. The default is a no-op.
    default :
        The value to use for array elements not in `mapping`. The
        default is to raise a `KeyError`. `None` is interpreted as a
        valid default.

    Returns
    -------
    mapped_array : array-like
        An array of the same shape as `arr`, with elements transformed
        according to the mapping.
    """
    def get(key):
        v = map.get(key, default)
        if v is Sentinel:
            raise KeyError(key)
        return v

    unq, ind = numpy.unique(arr, return_inverse=True)
    if value:
        vals = [value(get(u)) for u in unq]
    else:
        vals = [get(u) for u in unq]
    return numpy.array(vals)[ind]

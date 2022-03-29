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
# Version: 27 Jan 2022: Moved mask2runs, runs2mask from math
# Version: 28 Mar 2022: Added iterate_dtype


"""
Utilities for manipulating non-computational aspects of numpy arrays.

Mathematical computations belong in :py:mod:`haggis.math`.
"""

from itertools import product
from math import ceil, log

import numpy

from . import Sentinel
from .numbers import digit_count


__all__ = [
    'isolate_dtype', 'iterate_dtype', 'map_array', 'mask2runs', 'runs2mask'
]


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


def iterate_dtype(arr, iterate_elements=False):
    """
    Generate each primitive sub-array of a complex datatype.

    The generator yields the array for each builtin dtype. The leading
    dimensions of each yielded array are `arr.shape` the trailing
    dimensions are determined by `iterate_elements` and the shapes
    present in each sub-dtype. Currently, only depth-first traversal is
    supported.

    Parameters
    ----------
    arr : numpy.ndarray
        Must have a `dtype` attribute.
    iterate_elements : bool
        If `True`, array elements of each dtype will be yielded
        separately. See `Examples` for more information.

    Examples
    --------
    Create a complex dtype and an array of zeros::

        >>> dt0 = np.dtype([('a', np.float32), ('b', np.int32, 2)])
        >>> dt = np.dtype([('x', np.bool_), ('y', dt0, 3)])
        >>> arr = np.zeros((3, 3), dt)

    When iterating without elements, the genrator does not descend into
    each sub-dtype consisting of primitives::

        >>> for v in iterate_dtype(arr):
        ...     print(v.dtype, v.shape)
        bool_ (3, 3)
        float32 (3, 3, 3)
        int32 (3, 3, 3, 2)

    When `iterate_elements` is set, the generator descends into the
    elements of each sub-dtype, even if they are primitive::

        >>> for v in iterate_dtype(arr, iterate_elements=True):
        ...     print(v.dtype, v.shape)
        bool_ (3, 3)
        float32 (3, 3)
        int32 (3, 3)
        int32 (3, 3)
        float32 (3, 3)
        int32 (3, 3)
        int32 (3, 3)
        float32 (3, 3)
        int32 (3, 3)
        int32 (3, 3)
    """
    dt = arr.dtype
    if dt.fields is None:
        yield arr
    elif iterate_elements:
        # look at the dtype in detail
        for fname, (ftype, _) in dt.fields.items():
            if ftype.subdtype is not None:
                for index in product(*(range(n) for n in ftype.shape)):
                    yield from iterate_dtype(arr[fname][(Ellipsis,) + index],
                                             iterate_elements=True)
            else:
                yield from iterate_dtype(arr[fname], iterate_elements=True)
    else:
        # let it happen transparently
        for field in dt.fields:
            yield from iterate_dtype(arr[field], iterate_elements=False)


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


def mask2runs(mask, return_lengths=False, return_borders=False):
    """
    Find the runs in a boolean mask.

    Parameters
    ----------
    mask : array-like
        Boolean mask. If not boolean, will be cast to bool.
    return_lengths : bool, optional
        Whether or not to return an array of lengths for each run.
    return_borders : bool, optional
        Whether or not to return an array of dtype `np.int8` containing
        1 at each run start and -1 past run ends. The default is False.

    Returns
    -------
    regions : numpy.ndarray (2, N)
        Array of indices for each run. First column is the location of
        the run start, second column is past the run end.
    borders : numpy.ndarray (mask.shape)
        Array of :py:obj:`numpy.int8` containing 1 at each run start,
        -1 past each run end, and zero elsewhere. Only returned if
        ``return_borders`` is `True`. ``np.cumsum(borders).view(bool)``
        is equivalent to ``mask``.
    """
    mask = numpy.asanyarray(mask).astype(bool, copy=False)
    borders = numpy.diff(numpy.r_[numpy.int8(0),
                                  mask.view(numpy.int8),
                                  numpy.int8(0)])
    indices = numpy.flatnonzero(borders).reshape(-1, 2)

    if return_lengths:
        lengths = numpy.diff(indices, axis=1).ravel()
        if return_borders:
            return indices, lengths, borders
        return indices, lengths
    elif return_borders:
        return indices, borders
    return indices


def runs2mask(runs, n=None):
    """
    Convert an Nx2 array of run indices, such as the return of
    :py:func:`mask2runs` into a boolean mask of size `n`.

    Parameters
    ----------
    runs : array-like
        A two-column array, the first column being inclusive start
        indices for each run, and the second being exclusive stop
        indices.
    n : int, optional
        The size of the mask to generate. If missing (None), the
        end of the last run is assumed (``runs[-1, 1]``).

    Return
    ------
    mask : numpy.ndarray
        A boolean array of length ``n`` with runs set to True.
    """
    runs = numpy.asanyarray(runs)
    if n is None:
        n = runs[-1, 1]
    mask = numpy.zeros(n, dtype=bool)
    view = mask.view(numpy.int8)

    # Assign start indices
    view[runs[:, 0]] = 1

    # Assign end indices
    ends = runs[:, 1]
    if ends[-1] == n:
        ends = ends[:-1]
    view[ends] = -1

    numpy.cumsum(view, out=view)
    return mask

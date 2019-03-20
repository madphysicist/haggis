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
Routines for dealing with file types.

The module names in this package generally correspond to the informal
name of the file type they deal with, or to the extension.
"""

from os.path import splitext

from ..recipes import is_ordered_subset as _is_ordered_subset
from ..string_util import check_value


__all__ = [
    'ensure_extension', 'insert_suffix', 'open_file', 'PreOpenedFile',
]


def ensure_extension(name, ext, partial_policy=None, partial_limit=None):
    """
    Verify that the name ends with the required extension, and
    update it if not.

    `name` is assumed to be a string. `ext` is the desired suffix,
    usually beginning with ``'.'``. If `name` aleady ends with `ext`,
    return it as-is. If not, the extension will either be appended or
    completed depending on `partial_policy` and `partial_limit`. The
    first character of `ext` is treated as the separator character. It
    must appear in `name` for any of the completions to work.

    Recognized values for `partial_policy` are as follows (case
    insensitive):

        None, 'none', ''
            No partial extensions are recognized. If `name='a.xls'` and
            `ext=.xlsx`, the result will be `a.xls.xlsx`. Similarly for
            `b.jpg`, `.jpeg`, the result will be `b.jpg.jpeg`.
        'append', '+'
            Existing extension can be extended by at most
            `partial_limit` characters to acheive the target. If
            `name='a.xls'` and `ext=.xlsx`, the result will be `a.xlsx`.
            However, for `b.jpg`, `.jpeg`, the result will be
            `b.jpg.jpeg`.
        'insert', '^'
            Existing extension can have up to `partial_limit` characters
            inserted anywhere to acheive the target. If `name='a.xls'`
            and `ext=.xlsx`, the result will be `a.xlsx`. Similarly, for
            `b.jpg`, `.jpeg`, the result will be `b.jpeg`.
        'strip', '-'
            The existing extension may be loner than the desired one, so
            up to `partial_limit` characters may be stripped off the end
            to match the target. If `name='a.xlsx'` and `ext=.xls`, the
            result will be `a.xls`. However, for `b.jpeg`, `.jpg`, the
            result will be `b.jpeg.jpg`.
        'remove', 'x'
            The existing extension may be longer than the desired one,
            so removing up to `partial_limit` characters anywhere in the
            name is allowed. If `name='b.jpeg'` and `ext=.jpg`, the
            result will be `b.jpg`. However, if `name=b.jpg` and
            `ext=.jpeg`, the result is `b.jpg.jpeg`
        'replace', 'r'
            Replace any existing extension with the provided one.
        'create', 'c'
            Create the extension only if one does not already exist.

    `partial_limit` determines the maximum number of characters that can
    be modified to achieve the target. If `None` or a number greater
    than the length of `ext` mean "any number". If zero, the result will
    be the same as for `partial_policy='none'` regardless of the actual
    value of `partial_policy`, unless `partial_policy` is 'replace',
    which completely ignores the limit.
    """
    if partial_policy is not None:
        partial_type = check_value(partial_policy, ensure_extension.modes,
                                   label='match policy')
    else:
        partial_type = None

    if name.endswith(ext):
        # This should handle the empty `ext` case as well
        return name

    # At this point, `ext` is guarantee to be non-empty
    index = name.rfind(ext[0])

    if index == -1 or partial_type in (None, '', 'none'):
        return name + ext
    # At this point, `name` is guaranteed to contain `ext[0]` at index

    if partial_type in ('create', 'c'):
        return name

    def right_size(longer=True):
        """
        True if `partial_limit` is `None`, or if `ext` at least as long
        as the suffix of `name`, but by no more than `partial_limit`
        characters. This means that the name can be appended/inserted to
        to get the desired extension.

        If `longer` is `False`, the sense of the comparison is reversed:
        `ext` must be shorter than the suffix so the name can be
        stripped/removed from to get the extension.
        """
        delta = len(ext) - (last - index)
        if not longer:
            delta = -delta
        return partial_limit is None or 0 <= delta <= partial_limit

    last = len(name) - 1
    replace = False
    if partial_type in ('append', '+'):
        if right_size(True) and ext.startswith(name[index:]):
            replace = True
    elif partial_type in ('insert', '^'):
        if right_size(True) and _is_ordered_subset(name[index:], ext):
            replace = True
    elif partial_type in ('strip', '-'):
        if right_size(False) and name[index:].startswith(ext):
            replace = True
    elif partial_type in ('remove', 'x'):
        if right_size(False) and _is_ordered_subset(ext, name[index:]):
            replace = True
    else: # partial_type == 'replace'
        replace = True

    if replace:
        return name[:index] + ext
    return name + ext


ensure_extension.modes = (
    'none', '', 'append', '+', 'insert', '^', 'strip', '-', 'remove', 'x',
    'replace', 'r', 'create', 'c',
)


def insert_suffix(filename, suffix, allow_duplicate=False):
    """
    Insert a suffix into the file name before the extension.

    Append the suffix if there is no extension. By default, if the
    suffix is already present, it is not duplicated.

    Parameters
    ----------
    filename : str or ~pathlib.path
        The name to modify.
    suffix : str
        The suffix to insert.
    allow_duplicate : bool
        If :py:obj:`True`, no check will be made to see if the suffix is
        already present. If :py:obj:`False` (the default), the suffix
        will only be inserted if not already present.

    Return
    ------
    inserted : str
        The modified name.
    """
    parts = splitext(filename)
    if allow_duplicate or not parts[0].endswith(suffix):
        return str(suffix).join(parts)
    return str(filename)


class PreOpenedFile:
    """
    A proxy class for file objects that does not open or close the file
    when `__enter__`, `__exit__` and `close` are invoked.

    This version of the usual context manager is useful when processing
    opened files along with strings.

    Note that this is not a general-purpose proxy that can be used for
    most objects because it does not define any special methods besides
    `__repr__`, `__enter__`, `__exit__` and `close` as class attributes.
    """
    def __init__(self, file):
        self.__file = file

    def __getattr__(self, name):
        """
        Passes through access to all missing attributes to the
        underlying file object.
        """
        return getattr(self.__file, name)

    def __repr__(self):
        """
        Returns a string representation of the underlying file.
        """
        return '{}({})'.format(__class__.__name__, repr(self.__file))

    def __enter__(self, *args, **kwargs):
        """ Returns this proxy object. """
        return self

    def __exit__(self, *args, **kwargs):
        """ Does nothing. """
        pass

    def close(self):
        """ Does nothing. """
        pass


def open_file(file, *args, **kwargs):
    """
    Return an open file-like object for the input.

    If the input is already a file-like object (not a string or file
    descriptor), a proxy for it is returned. The original object remains
    unmodified. The proxy can be used in a context manager, but it will
    not close the file when exiting.

    Strings and file descriptors are opened using the additional
    arguments provided. They return a true file object that will close
    itself when used as a context manager.

    Returns
    -------
    file : file-like
        A file-like opened from the `file` input.
    """
    # Checking for file vs descriptor
    try:
        return open(file, *args, **kwargs)
    except TypeError:
        return PreOpenedFile(file)

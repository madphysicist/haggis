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
# Version: 11 Feb 2021: Added package_root


"""
Functions for manipulating the structure of objects.

This includes things like spoofing module contents, copying classes and
functions, and automatically creating properties.
"""

from copy import copy
from functools import update_wrapper, WRAPPER_ASSIGNMENTS
import sys
from types import FunctionType, ModuleType


__all__ = [
    'HiddenPropMeta', 'package_root', 'update_module',
    'copy_func', 'copy_class'
]


def package_root(module):
    """
    Find the directory containing the root package in which a module is
    defined.

    Only works for modules with a valid ``__file__`` attribute.

    Parameters
    ----------
    module : str or ~types.ModuleType
        The module to investigate. If a name is passed in, the module
        must exist in :py:attr:`sys.modules`.

    Return
    ------
    path : str
        The root path of the package containing the module.
    """
    if isinstance(module, str):
        module = sys.modules[module]
    name = module.__name__
    path = module.__file__
    if basename(path) == '__init__.py':
        path = dirname(path)
    for _ in range(name.count('.') + 1):
        path = dirname(path)
    return path


def update_module(current, other, recurse=False):
    """
    Updates the dict of the module `current` with the dict of
    `other`.

    Either input may be a string (full name as given by ``__name__``),
    or a module reference.

    All functions and classes in `other` whose module is `other`
    will by default be copied and reassigned to `current`. All other
    non-dunder attributes will be copied exactly. Dunder attributes will
    be skipped, except ``__all__``, which will be shallow-copied as a
    list.

    Any attributes already defined in `current` will be skipped. This
    ensures that the globals defined in new methods will be updated
    correctly for the new module.

    If `recurse` is set to :py:obj:`True`, any sub-modules of `other`
    will be copied using this method instead of referenced directly.
    """
    def getmod(mod):
        if isinstance(mod, str):
            return sys.modules[mod]
        # Ducktype non-string objects. This allows things like
        # classes spoofing a module to pass through just fine.
        return mod
    current = getmod(current)
    other = getmod(other)
    cn, on = current.__name__, other.__name__
    cd = current.__dict__
    for name, item in other.__dict__.items():
        if name in cd:
            continue
        if name.startswith('__') and name.endswith('__'):
            if name == '__all__':
                try:
                    item = item[:]
                except Exception:
                    pass
            else:
                continue
        elif isinstance(item, FunctionType):
            if item.__module__ == on:
                item = copy_func(item, cd, cn)
        elif isinstance(item, type):
            if item.__module__ == on:
                item = copy_class(item, cd, cn)
        elif isinstance(item, ModuleType) and recurse:
            if item.__name__.startswith(on + '.'):
                mod = ModuleType(item.__name__.replace(on, cn), item.__doc__)
                update_module(mod, item, recurse)
                sys.modules[mod.__name__] = mod
                item = mod
        cd[name] = item


def copy_class(c, globals=None, module=None):            
    """
    Creates a shallow copy of a class object, optionally replacing
    its module and the object its methods reference for globals.

    This function is useful when importing a class into another
    module, and having it behave as a class of the importing module::

        from mod import cls
        cls = copy_class(cls, globals(), __name__)

    Parameters
    ----------
    c : type
        The class to copy
    globals : dict or None
        If :py:obj:`None`, copy the global dictionaries referenced by
        the methods unchanged. A popular alternative is ``globals()``.
    module : str or None
        The name of the module that this class belongs to. If
        :py:obj:`None`, keep ``c.__module__`` and the modules of all
        methods directly. A popular alternative is ``__name__``.

    Notes
    -----
    This function may not work properly for classes whose metaclass does
    not invoke :py:meth:`type.new <object.__new__>` at some point in the
    construction process.

    Based on https://stackoverflow.com/a/49157516/2988730.
    """
    if module is None:
        module = c.__module__
    attrs = dict(c.__dict__)
    for name, item in c.__dict__.items():
        if isinstance(item, type):
            attrs[name] = copy_class(item, globals, module)
        elif isinstance(item, FunctionType):
            attrs[name] = copy_func(
                item, item.__globals__ if globals is None else globals, module
            )
    d = type.__new__(type(c), c.__name__, c.__bases__, attrs)
    d.__module__ = module
    return d


def copy_func(f, globals=None, module=None):
    """
    Creates a shallow copy of a function object, optionally replacing
    the object it references for its globals.

    This function is useful when importing a function into another
    module, and having it behave as a function of the importing module::

        from mod import func
        func = copy_func(func, globals(), __name__)

    Parameters
    ----------
    f : function
        The object to copy
    globals : dict or None
        If :py:obj:`None`, copy the global dictionary referenced by
        `f`. A popular alternative is ``globals()``.
    module : str or None
        The name of the module that this function belongs to. If
        :py:obj:`None`, copy ``f.__module__`` directly. A popular
        alternative is ``__name__``.

    Notes
    -----
    Based originally on https://stackoverflow.com/a/13503277/2988730,
    and updated in https://stackoverflow.com/a/49077211/2988730.
    """
    g = FunctionType(f.__code__, f.__globals__ if globals is None else globals,
                     name=f.__name__, argdefs=f.__defaults__,
                     closure=f.__closure__)
    g = update_wrapper(g, f)
    if module is not None:
        g.__module__ = module
    g.__kwdefaults__ = copy(f.__kwdefaults__)
    return g


class HiddenPropMeta(type):
    """
    Creates a class with "hidden" read-only properties named in the
    :py:attr:`__hidden_properties__` attribute.

    A hidden property is one that stores its value under a 
    :py:attr:`~object.__dict__` key with the same name. This meta-class
    is therefore incompatible with anything that uses
    :py:obj:`~object.__slots__`.

    .. py:attribute:: __hidden_properties__

       This can be a single string, an iterable of strings, or an
       iterable of two-element tuples containing a string name and an
       initial value. Strings and tuples may be mixed together in an
       iterable. The attribute will be removed from the class body by
       this metaclass after it is processed.

    If the class has an explicit ``__init__`` method defined, it will be
    properly decorated to set the default values of the hidden
    properties. If an explicit ``__init__`` is not found, the implicit
    ``super.__init__`` constructor will be decorated in the same way and
    set as the initializer.
    """
    def __new__(meta, name, bases, body, **kwargs):
        if '__hidden_properties__' in body:
            props = body['__hidden_properties__']
            del body['__hidden_properties__']
            if isinstance(props, str):
                props = [props]

            def check_prop(prop):
                """
                Check if `prop` is a string or a 2-element tuple and
                returns a 2-element tuple. The first element must be a
                string, the second defaults to :py:obj:`None`.
                """
                if isinstance(prop, str):
                    return (prop, None)
                if not isinstance(prop, tuple) or len(prop) != 2 or \
                   not isinstance(prop[0], str):
                    raise ValueError(
                        'property description must be name or name-value tuple'
                    )
                return prop

            props = dict(check_prop(prop) for prop in props)

            def fget(name):
                """
                Create the getter for a given property name.
                """
                def getter(self):
                    return self.__dict__[name]
                getter.__name__  = name
                getter.__doc__ = f'Retrieves {name} as a read-only property.'
                return getter

            for prop in props:
                if prop not in body:
                    body[prop] = property(fget(prop))
                elif not isinstance(body[prop], property):
                    raise ValueError(
                        'property {!r} shadows non-property '
                        'attribute'.format(prop)
                    )
        else:
            props = None

        cls = super().__new__(meta, name, bases, body)
        if props:
            def wrapper(parent, initializer):
                def  __init__(self, *args, **kwargs):
                    self.__dict__.update(initializer)
                    return parent(self, *args, **kwargs)

                update_wrapper(
                    __init__, parent, tuple(
                        x for x in WRAPPER_ASSIGNMENTS if x != '__qualname__'
                    )
                )
                __init__.__qualname__ = '.'.join(
                    (cls.__qualname__, '__init__')
                )
                return __init__
            setattr(cls, '__init__', wrapper(getattr(cls, '__init__'), props))
        return cls

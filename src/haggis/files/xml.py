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
Utilities for extending and configuring the Python XML framework.
"""

__all = ['SAXBase', 'SAXLogger', 'SAXLoggable']


from logging import LoggerAdapter
from xml.sax.handler import ContentHandler

from ..logs import MetaLoggableType


class SAXBase(ContentHandler):
    """
    An empty SAX parser with some convenience functionality built in.

    This class provides a reference to the locator. All of the actual SAX
    callback methods are currently no-ops.
    """
    def __init__(self):
        """
        Initialize the base classes and set the locator to `None`.
        """
        super().__init__()
        self.locator = None

    def setDocumentLocator(self, locator):
        """
        Set the locator used in error reporting.

        The locator can be accessed through the :py:meth:`locate`
        message-reformatting utility method.
        """
        self.locator = locator

    def _get_position(self):
        """
        Retrieve the position based on the currently configured locator.

        If there is no locator set, the position will be NaN.
        """
        if self.locator is None:
            return (float('nan'),) * 2
        return self.locator.getLineNumber(), self.locator.getColumnNumber()

    def locate(self, message, *args, short=False):
        """
        Convert a message and argument-list to a message with location
        information, and extends the argument list appropriately.

        Return a tuple containing two elements: the message and the
        argument list as a single tuple that can be expanded into the
        argument of any of the logging methods.

        The full version of the location string (default) includes the
        file name, the line number and the column. The short version
        only inculdes the line number and column.
        """
        if short:
            message += ' on line %d:%d'
            extra = self._get_position()
        else:
            message += ' in %s:%d:%d'
            extra = (self.locator.getSystemId(), *self._get_position())
        return (message, (*args, *extra))

    def short_locate(self, message, *args):
        """
        Identical to :py:meth:`locate`, except that the file name is not
        included in the updated message.
        """
        return (message + ' on line %d:%d', (*args, *self._get_position()))


class SAXLogger(LoggerAdapter):
    """
    A logger adapter class that adds location information to the
    messages when a locator is set.

    The location information is inserted into the log formatter via the
    `extra` keyword argument, so it can be accessed through the names
    ``sax-file``, ``sax-line`` and ``sax-column``.

    .. py:attribute:: logger

       The underling :py:class:`~logging.Logger` that messages go to.

    .. py:attribute:: locator

       The locator that determines the position within the document. If
       not set, messages will be left intact and extra information will
       be set to :py:obj:`None`.

    .. py:attribute:: long

       Indicates that the position information should be presented in
       long format. Defaults to :py:obj:`True`. Set to :py:obj:`None` to
       disable modification of the message except by the formatter.
    """
    #: Mapping of the locator keywords allowed in long messages to
    #: locator attributes.
    _keys = {
        'file': lambda locator: locator.getSystemId(),
        'line': lambda locator: locator.getLineNumber(),
        'column': lambda locator: locator.getColumnNumber()
    }

    #: Default prefix for the keys. Overriding this value will change
    #: the names under which locator information is made available.
    _prefix = 'sax-'

    def __init__(self, logger, locator=None, long=True):
        """
        Initialize this adapter around the specified logger.
        """
        self.locator = locator
        self.long = True
        super().__init__(logger, extra=SAXLogger.LocatorExtra(locator))

    @property
    def long(self):
        """
        Whether or not this adapter displays location information in
        long mode (defaults to :py:obj:`True`).

        The file information is appended in long mode but not in short
        mode.
        """
        return self.__dict__['long']

    @long.setter
    def long(self, value):
        self.__dict__['long'] = value if value is None else bool(value)

    def _location(self, prefix=''):
        """
        Get the location information with an arbitrary prefix before the
        key names.
        """
        return {
            prefix + k: None if self.locator is None else v(self.locator)
            for k, v in self._keys.items()
        }

    @property
    def location(self):
        """
        The location information as a dynamically-generated dictionary.

        If no locator is set, all the values are :py:obj:`None`.
        """
        return self._location(self._prefix)

    def process(self, msg, kwargs):
        """
        Add either long or short location information to the message,
        based on the current setting of :py:attr:`long` and whether or
        not a locator is set.

        Always insert location information into ``kwargs`` for the
        formatter to use, but don't insert into a log message unless
        there is a valid locator.
        """
        if self.locator is not None and self.long is not None:
            # Illegible one-liner:
            # return [self.process_short, self.process_long][self.long](msg,
            #                                                           kwargs)
            if self.long:
                return self.process_long(msg, kwargs)
            return self.process_short(msg, kwargs)
        return msg, self.update_kwargs(kwargs)

    def process_long(self, msg, kwargs):
        """
        Add long-formatted location information to the message.

        Insert location information into ``kwargs`` through the
        ``'extra'`` key.
        """
        msg += ' in {file}:{line}:{column}'.format(**self._location())
        return msg, self.update_kwargs(kwargs)

    def process_short(self, msg, kwargs):
        """
        Add short-formatted location information to the message.

        Insert location information into ``kwargs`` through the
        ``'extra'`` key.
        """
        msg += ' on line {line}:{column}'.format(**self._location())
        return msg, self.update_kwargs(kwargs)

    def update_kwargs(self, kwargs):
        """
        Add an ``'extra'`` item to ``kwargs`` containing a dictionary
        with current location information.

        Any existing ``'extra'`` in ``kwargs`` will be merged with the
        location information, with existing keys overriding similarly
        named location keys.

        Return the input argument after update.
        """
        kwargs['extra'] = self.location().update(kwargs.get('extra', {}))
        return kwargs


class SAXLoggable(SAXBase, metaclass=MetaLoggableType):
    """
    A type of :py:class:`SAXBase` that provides logging in addition to
    location methods.
    """
    def log(self, level, msg, *args, **kwargs):
        """
        Append location information to a log message.

        This method allows an additional keyword argument `short` that
        determines whether or not the full file name will be present in
        the location. `short` is :py:obj:`True` by default, meaning that
        only the line and column number are reported.
        """
        short = kwargs.pop('short', 'True')
        msg, args = self.locate(msg, *args, short=short)
        self.logger.log(level, msg, *args, **kwargs)

    def setDocumentLocator(self, locator, level=None):
        """
        Set the locator used in error reporting and log it, with
        location.

        Logging is done using :py:meth:`log`. The locator will not be
        logged if `level` is :py:obj:`None`.
        """
        super().setDocumentLocator(locator)
        if level is not None:
            self.log(level, "Set document locator")

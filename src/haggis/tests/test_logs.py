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
# Version: 01 Nov 2022: Initial Coding


"""
Tests for the :py:mod:`haggis.logs` module.
"""


from contextlib import contextmanager
from io import StringIO
import logging

from pytest import fixture, raises

from ..logs import (
    KEEP, KEEP_WARN, OVERWRITE, OVERWRITE_WARN, RAISE,
    reset_handlers, LogMaxFilter, MetaLoggableType 
)

class LoggingTestBase(metaclass=MetaLoggableType):
    levelNames = {
        lvl: logging.getLevelName(lvl) for lvl in (
            logging.DEBUG, logging.INFO, logging.WARNING,
            logging.ERROR, logging.CRITICAL
        )
    }

    @fixture
    def reset_handler(self):
        return True

    @fixture
    def initial_level(self):
        return logging.DEBUG

    @fixture
    def formatter(self):
        return logging.Formatter('%(levelname)s %(message)s')

    @fixture
    def log_setup(self, initial_level, reset_handler, formatter):
        self.stream = StringIO()
        self.handler = logging.StreamHandler(self.stream)
        if reset_handler:
            reset_handlers(self.handler, logger=self.logger,
                           level=initial_level, format=formatter)
        else:
            self.handler.setFormatter(formatter)
            self.handler.setLevel('NOTSET')
            self.logger.addHandler(self.handler)
        self.logger.setLevel(initial_level)


class TestLogMaxFilter(LoggingTestBase):
    @fixture
    def reset_handler(self):
        return False

    @contextmanager
    def temp_log_max_filter(self, obj, *args, **kwargs):
        filter = LogMaxFilter(*args, **kwargs)
        obj.addFilter(filter)
        yield
        obj.removeFilter(filter)
        self.handler.flush()

    def test_inclusive_logger(self, log_setup):
        with self.temp_log_max_filter(self.logger, 'WARNING', inclusive=True):
            for value, name in self.levelNames.items():
                self.logger.log(value, name)

        text = self.stream.getvalue()
        for value, name in self.levelNames.items():
            if value >= logging.WARNING:
                assert name not in text
            else:
                assert ' '.join((name, name)) in text

    def test_exclusive_logger(self, log_setup):
        with self.temp_log_max_filter(self.logger, logging.WARNING,
                                      inclusive=False):
            for value, name in self.levelNames.items():
                self.logger.log(value, name)

        text = self.stream.getvalue()
        for value, name in self.levelNames.items():
            if value > logging.WARNING:
                assert name not in text
            else:
                assert ' '.join((name, name)) in text

    def test_inclusive_handler(self, log_setup):
        with self.temp_log_max_filter(self.handler, logging.WARNING,
                                      inclusive=True):
            for value, name in self.levelNames.items():
                self.logger.log(value, name)

        text = self.stream.getvalue()
        for value, name in self.levelNames.items():
            if value >= logging.WARNING:
                assert name not in text
            else:
                assert ' '.join((name, name)) in text

    def test_exclusive_handler(self, log_setup):
        with self.temp_log_max_filter(self.handler, 'WARNING',
                                      inclusive=False):
            for value, name in self.levelNames.items():
                self.logger.log(value, name)

        text = self.stream.getvalue()
        for value, name in self.levelNames.items():
            if value > logging.WARNING:
                assert name not in text
            else:
                assert ' '.join((name, name)) in text

        self.handler.removeFilter(filter)


    def test_custom_level(self, log_setup):
        with self.temp_log_max_filter(self.logger, logging.WARNING + 5,
                                      inclusive=False):
            for value, name in self.levelNames.items():
                self.logger.log(value, name)

        text = self.stream.getvalue()
        for value, name in self.levelNames.items():
            if value > logging.WARNING:
                assert name not in text
            else:
                assert ' '.join((name, name)) in text

    def test_bad_level(self, log_setup):
        raises(TypeError, LogMaxFilter, '_NOTALEVEL32', inclusive=True)
        raises(TypeError, LogMaxFilter, '_NOTALEVEL32', inclusive=False)


class TestMetaLoggableType:
    def test_regular(self):
        class Test(metaclass=MetaLoggableType):
            namespace = 'xxx'

        expected_name = Test.__module__ + '.' + Test.__qualname__

        assert not hasattr(Test, '__namespace__')
        assert isinstance(Test.logger, logging.Logger)
        assert Test.logger.name == expected_name
        assert logging.getLogger(expected_name) is Test.logger

    def test_namespace(self):
        class Test(metaclass=MetaLoggableType):
            __namespace__ = 'xxx'

        expected_name = Test.__namespace__ + '.' + Test.__module__ + '.' + Test.__qualname__

        assert hasattr(Test, '__namespace__')
        assert isinstance(Test.logger, logging.Logger)
        assert Test.logger.name == expected_name
        assert logging.getLogger(expected_name) is Test.logger

    def test_builtin(self):
        """ Verify that builtins play nicely with the metaclass. """
        class Test(list, metaclass=MetaLoggableType):
            __namespace__ = 'xyz'

        expected_name = Test.__namespace__ + '.' + Test.__module__ + '.' + Test.__qualname__

        assert hasattr(Test, '__namespace__')
        assert isinstance(Test.logger, logging.Logger)
        assert Test.logger.name == expected_name
        assert logging.getLogger(expected_name) is Test.logger

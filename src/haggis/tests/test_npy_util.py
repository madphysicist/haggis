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
# Version: 01 Jun 2022: Initial Coding


"""
Tests for the :py:mod:`haggis.npy_util` module.
"""


import numpy as np
from pytest import raises

from ..npy_util import replace_field


class TestReplaceField:
    inner = np.dtype([('Roll', np.float32),
                      ('Pitch', np.float32),
                      ('Yaw', np.float32)])
    inner2 = np.dtype([('RollPitchYaw', np.float32, 3)])
    outer = np.dtype([('Position', np.float32, 3),
                      ('Attitude', inner)])
    outer2 = np.dtype([('Position', np.float32, 3),
                       ('Attitude', np.float32, 3)])

    def test_replace_custom(self):
        result = replace_field(self.outer, np.float32, 'Attitude')
        expected = self.outer2
        assert result == expected

    def test_replace_with_custom(self):
        result = replace_field(self.outer2, self.inner, 'Attitude')
        assert result == self.outer

    def test_empty_fields(self):
        result = replace_field(self.inner, np.float32)
        expected = self.inner2
        assert result == expected

    def test_name(self):
        dt = np.dtype([('snake', np.float32),
                       ('toSnake', np.float32),
                       ('toCamel', np.float32),
                       ('ToCAMEL', np.float32),
                       ('X', np.float32)])

        result = replace_field(dt, np.float32, name='RPY')
        expected = np.dtype([('RPY', np.float32, 5)])
        assert result == expected

        expected = np.dtype([('snake_toSnake_toCamelToCAMEL_X', np.float32, 5)])
        result = replace_field(dt, np.float32)

    def test_order(self):
        result = replace_field(self.inner, np.float32, 'Roll', 'Pitch', 'Yaw')
        expected = np.dtype([('RollPitchYaw', np.float32, 3)])
        assert result == expected

        result = replace_field(self.inner, np.float32, 'Yaw', 'Pitch', 'Roll')
        expected = np.dtype([('YawPitchRoll', np.float32, 3)])
        assert result == expected

    def test_nested(self):
        result = replace_field(
            self.outer, replace_field(self.inner, np.float32), 'Attitude'
        )
        expected = np.dtype([
            ('Position', np.float32, 3), ('Attitude', self.inner2)
        ])
        assert result == expected

    def test_span(self):
        result = replace_field(self.inner, np.float64, 'Yaw', 'Pitch')
        expected = np.dtype([('Roll', np.float32),
                             ('YawPitch', np.float64)])
        assert result == expected

        raises(ValueError, replace_field, self.inner, np.float64, 'Yaw', 'Roll')

    def test_align(self):
        spec = [('a', np.int32), ('b', np.int8), ('c', np.int32)]
        dt = np.dtype(spec, align=True)

        result = replace_field(dt, np.int8, 'b')
        expected = dt
        assert result == expected

        result = replace_field(dt, np.int8, 'b', 'c')
        expected = np.dtype([('a', np.int32), ('b_c', np.int8, 8)])
        assert result == expected

        dt = np.dtype(spec, align=False)

        result = replace_field(dt, np.int8, 'b')
        expected = dt
        assert result == expected

        result = replace_field(dt, np.int8, 'b', 'c')
        expected = np.dtype([('a', np.int32), ('b_c', np.int8, 5)])
        assert result == expected

    def test_union(self):
        result = replace_field(self.inner, np.float32, 'Yaw', 'Roll')
        expected = np.dtype({
            'names': ['YawRoll', 'Pitch'],
            'formats': [(np.float32, 3), np.float32],
            'offsets': [0, 4],
            'itemsize': 12,
        })
        assert result == expected

    def test_nofields(self):
        raises(ValueError, replace_field, np.dtype(np.float32), np.float32)

    def test_missing(self):
        raises(ValueError, replace_field, self.inner, np.float32, 'XXX')

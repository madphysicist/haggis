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
# Version: 09 Jan 2021: Added to_hex, camel2snake, snake2camel, timestamp
# Version: 11 Feb 2021: Moved timestamp to module time
# Version: 30 Mar 2022: Bugfix in [split_]align and [split_]horiz_cat to enforce strings


"""
Utilities for creating, chopping, concatenating and otherwise processing
strings.

The functions in this module that operate on multi-line strings have
versions that start with ``split_``, which accept iterables of lines
instead of entire strings.
"""

__all__ = [
    'hasspace',
    'format_list',
    'align', 'split_align',
    'horiz_cat', 'split_horiz_cat',
    'make_box', 'register_box_style',
    'check_value',
    'to_casefold', 'to_lower', 'to_upper', 'to_hex',
    'camel2snake', 'snake2camel',
]


from collections import deque, namedtuple
from itertools import chain, repeat
from math import ceil
from operator import index
from os import linesep

from .mapping import option_lookup
from .recipes import grouper, shift_left


def hasspace(x):
    """
    Check if string `x` contains a space.

    If `x` is not a string, and is not Falsy, it is coerced into a
    string. Falsy inputs never have spaces (according to this function).
    """
    if not x:
        return False
    x = str(x)
    s = x.split()
    return len(s) != 1 or x != s[0]


def format_list(iterable, width=8, format=None, sep=', ', indent=None):
    """
    Display the elements of the iterable, `width` elements per line.

    Parameters
    ----------
    iterable : iterable
        The iterable to pretty-print.
    width : int
        The number of elements to print per line. Defaults to 8. If
        :py:obj:`None`, the entire list will appear on one line.
    format : str
        A new-style format string to represent each value. Defaults to
        ``'{}'``.
    sep : str
        The separator to place between entries on the same line.
        Defaults to ``', '``.
    indent : int or str
        If :py:class:`int`, the number of spaces by which to indent each
        line of the input. If a :py:class:`str`, act as a literal prefix
        to each line. Defaults to ``4`` unless ``width`` is
        :py:obj:`None`, in which case the default is an empty string.

    Return
    ------
    formatted_data : str
        A string containing the formatted data.
    """
    if format is None:
        format = '{}'

    if indent is None:
        indent = '' if width is None else 4

    try:
        spacer = ' ' * index(indent)
    except TypeError:
        spacer = str(indent)

    if width is None:
        result = sep.join(format.format(x) for x in iterable)
    else:
        joiner = sep.rstrip() + '\n' + spacer
        result = joiner.join(sep.join(format.format(x) for x in group)
                             for group in grouper(iterable, width))

    return spacer + result


def _maxlen(lines, len_key=len):
    """
    Return the maximum length in an iterable based on the specified
    length function.
    """
    return max(len_key(line) for line in lines) if lines else 0


#: Mapping of acceptable alignments inputs to :py:func:`align`,
#: :py:func:`horiz_cat` and :py:func:`print_box`.
_alignments = {
    "left": '<',   "<": '<',
    "center": '^', "^": '^',
    "right": '>',  ">": '>',
    "none": None,  "": None, None: None,
}


#: Mapping of acceptable overflow handling options to :py:func:`align`.
#: The :py:obj:`None` key represents callables. The values are a
#: function that accepts an iterable of lines and a width and returns
#: the updated lines and width with overflow handled. Any overflow lines
#: are expected to be handled with the ``'skip'`` algorithm after that.
_align_overflow = {
    "extend": lambda lines, width, len, trunc: \
        (list(lines), max(width, _maxlen(lines, len))),
    "trunc": lambda lines, width, len, trunc: \
        ([line[:width] for line in lines], width),
    "skip": lambda lines, width, len, trunc: (lines, width),
    None: lambda lines, width, len, trunc: \
        ([trunc(line) for line in lines], width),
}


#: Mapping of normalized alignments (obtained from
#: :py:data:`_alignments`) to a function of ``string`` and ``delta``
#: that formats the string with additional padding adding a total of
#: ``delta`` spaces to it. ``delta`` is always expected to be positive.
_align_fn = {
    "<": lambda string, delta: '{}{}'.format(string, ' ' * delta),
    ">": lambda string, delta: '{}{}'.format(' ' * delta, string),
    "^": lambda string, delta: '{}{}{}'.format(' ' * (delta // 2), string,
                                               ' ' * ((delta + 1) // 2)),
}


def align(string, *args, **kwargs):
    """
    Align a string in a space-padded field of the specified width.

    This function differs from just doing something like ::

        {0:{1}{2}}.format(string, alignment, width)

    because the "actual" length of the string is computed by
    `len_key` rather than the builtin :py:func:`len`. It also
    correctly handles multiline strings.

    Parameters
    ----------
    string : str
        The string to align. May contain multiple lines.
    alignment : str or None
        A value that indicates how to align lines. Recognized options
        are as follows:

        ``'left'`` or ``'<'``
            `string` is padded on the right to `width`.
        ``'center'`` or ``'^'``
            `string` is padded equally on each side to `width`.
        ``'right'`` or ``'>'``
            `string` is padded on the left to `width`.
        ``'none'``, ``''`` or ``None``
            `string` is returned as-is, regardless of `width`.

    width : int or None
        The minimum field width to align in. If :py:obj:`None`, use the
        maximum line length as the field width. :py:obj:`None` does not
        make much sense for a single-line string: it will just be
        returned as-is. If `width` is shorter than *any* of the lines,
        it will have no effect.
    overflow : str or callable
        How to handle overflow lines (wider than width). The following
        options are accepted:

        ``'extend'``
            The effective width will be the largest of the maximum line
            length and `width`. This is the default.
        ``skip``
            Skip longer lines, but align shorter ones to `width`.
        ``'trunc'``
            Truncate to `width`. This may not work correctly if
            `len_key` is not the builtin function :py:func:`len`.
            Use the callable option in that case.
        ``callable``
            A function that accepts long input lines and returns a
            truncated line. This can do special truncation or any other
            operation the user desires. The result will be aligned using
            ``overflow=skip`` in this case. The callable will only be
            applied to overflow lines.

        This parameter is completely ignored if `width` is
        :py:obj:`None`.
    len_key : callable
        A custom callable for computing the lengths of strings. This can
        be useful for example if the strings contain tabs or some
        similar sequence whose display width is not necessarily the raw
        string width. Defaults to the builtin :py:func:`len`.

    Return
    ------
    aligned : str
        `string` aligned in a field of size `width` according to the
        spec. If the input string is greater than or equal to `width`
        in length, it is returned as-is.
    """
    return '\n'.join(split_align(str(string).splitlines(), *args, **kwargs))


def split_align(strings, alignment, width=None, overflow='extend',
                len_key=len):
    """
    Identical to :py:func:`align` except that the lines are passed in
    as an iterable instead of a single string.

    The result is a list of lines rather than a single string.
    """
    strings = [str(s) for s in strings]
    if width is None:
        width = _maxlen(strings, len_key)
    overflow_fn = option_lookup(
        'overflow', _align_overflow, overflow,
        key_func=lambda x: None if callable(x) else str(x).casefold()
    )
    strings, width = overflow_fn(strings, width, len_key, overflow)
    deltas = [width - len_key(string) for string in strings]

    # Normalize alignment
    alignment = option_lookup('alignment', _alignments, alignment,
                              key_func=lambda opt: str(opt).casefold())

    if not alignment:
        return strings
    formatter = _align_fn[alignment]

    strings = [formatter(string, delta) if delta >= 0 else string
               for string, delta in zip(strings, deltas)]
    return strings


#: Mapping of accepted values for :py:func:`horiz_cat`'s `missing`
#: parameter to list indices. Numerical keys get mapped to
#: :py:obj:`None`.
_hc_missing = {
    'down': None,
    'missing': None,
    'trunc': None,
    'empty': '',
    'first': 0,
    'last': -1,
    None: None,
}


def horiz_cat(*strings, **kwargs):
    """
    Concatenate multi-line strings side-by-side.

    For single line strings, this function is equivalent to
    ``prefix + sep.join(*strings) + suffix``.

    Parameters
    ---------
    *strings : list[str]
        Any number of strings. This function is pointless if none of
        the strings have more than one line, but multiple lines are not
        a requirement.
    prefix : str
        A prefix that will be prepended to each line of the result. This
        can be used to do indentation, among other things. Default is
        empty.
    sep : str
        The separator to insert between columns. The separator will be
        omitted around empty columns if ``missing='missing'``. Default
        is a single space.
    suffix : str
        A suffix that will be added to each line in the result. Default
        is empty.
    linesep : str
        The line separator to use. The default is :py:obj:`os.linesep`.
    alignment : str, sequence[str] or None
        A value that indicates how to align strings. Acceptable
        values are as follows:

        ``'left'`` or ``'<'``
            Each string is padded on the right to the length of the
            maximum line length. Shorter lines are left aligned.
        ``'center'`` or ``'^'``
            Each string is padded equally on each side to the length of
            the maximum line length. Shorter lines are center aligned.
        ``'right'`` or ``'>'``
            Each string is padded on the left to the length of the
            maximum line length. Shorter lines are right aligned.
        ``'none'`` or ``None``
            Strings are not padded at all, just concatenated as-is.

        If a sequence if passed in, it must contain as many elements as
        `strings`. Each column in `strings` will be aligned according to
        the corresponding alignment. Having ``'none'`` elements is not
        strictly forbidden in this case, but it may completely throw off
        the formatting of the following columns.

        The default is ``'<'``.
    missing : str or int
        A specification for how to handle strings with fewer lines than
        the others. This does not apply to empty lines within the
        string. Acceptable values are as follows:

        ``'down'``
            Shift all shorter inputs down using empty lines.
        ``'trunc'``
            Truncate all inputs to the smallest number of lines.
        ``'empty'``
            The default is to treat missing lines as through they are
            empty lines. All alignement rules apply.
        ``'missing'``
            Remove missing lines entirely, and shift further columns to
            the left. The corresponding line of the following string
            will affect the column width of this string if applicable
            because of the shift.
        ``'last'``
            Repeat the last line.
        ``'first'``
            Repeat the first line. A synonym for ``missing=0``.
        integer or string that evaluates to integer
            Repeat the n-th line. Use this carefully as it will raise an
            error if any of the strings have fewer than ``n+1`` lines.
    len_key : callable
        A custom callable for computing the lengths of strings. This can
        be useful for example if the strings contain tabs or some
        similar sequence whose display width is not necessarily the raw
        string width. Defaults to the builtin :py:func:`len`.

    Return
    ------
    cat : str
        A string that is a side-by-side concatenation of the inputs
        given the selected options.

    Raises
    ------
    ValueError:
        If `justification` or `missing` are set to invalid values.
    IndexError:
        If `missing` is an integer or a string that parses as an
        integer but one of the input strings does not contain the
        specified line index.
    """
    # Arrange columns as 2D list
    columns = [string.splitlines() for string in strings]
    return split_horiz_cat(*columns, **kwargs)


def split_horiz_cat(*columns, prefix='', sep=' ', suffix='', linesep=linesep,
                    alignment='<', missing='empty', len_key=len):
    """
    Identical to :py:func:`horiz_cat`, except the inputs are sequences
    of strings already split into lines.

    If `linesep` is :py:obj:`None`, the output will not be combined
    into a string, but will be returned as a :py:class:`list` instead.
    """
    maxlines = _maxlen(columns, len_key=len)

    # Handle missing elements
    def missing_key(option):
        try:
            int(missing)
        except:
            if isinstance(missing, str):
                return missing.casefold()
            return False  # Known to be invalid key
        else:
            return None

    def missing_value(option, key, value):
        down = False
        if key is None:
            fn = lambda col: col[int(option)]
        elif key == 'down':
            down = True
            fn = lambda col: ''
        elif key == 'missing':
            # Shift left is necessary for widths to be computed correctly
            return shift_left(*columns)
        elif key == 'trunc':
            return list(map(list, columns))
        elif isinstance(value, int):
            fn = lambda col: col[value]
        else:
            fn = lambda col: value

        def args(col):
            rep = repeat(fn(col), maxlines - len(col))
            if down:
                return rep, col
            return col, rep
        return [list(chain(*args(col))) for col in columns]

    if isinstance(alignment, (type(None), str)):
        alignment = [alignment] * len(columns)
    elif len(alignment) != len(columns):
        raise IndexError('Number of alignments ({}) does not match number of '
                         'columns ({})'.format(len(alignment), len(columns)))

    columns = option_lookup('missing', _hc_missing, missing,
                            key_func=missing_key, value_func=missing_value)
    columns = [split_align(column, alignment=align, len_key=len_key)
               for align, column in zip(alignment, columns)]
    lines = [prefix + sep.join(items) + suffix for items in zip(*columns)]

    if linesep is None:
        return lines
    return linesep.join(lines)


#: Styles available to :py:func:`make_box`, keyed by name.
_make_box_styles = {}


#: The values of :py:data:`_make_box_styles`.
_make_box_style = namedtuple('_make_box_style', [
    'top', 'left', 'bottom', 'right', 'ul', 'ur', 'bl', 'br'])


def make_box(string, style='ascii-block', alignment='^', linesep=linesep,
             horizontal_padding=1, vertical_padding=0, len_key=len):
    """
    Surrounded the input string by a box.

    Parameters
    ----------
    string : str
        A string, which may contain multiple lines.
    style : str
        The type of box to draw. Styles are registered with
        :py:func:`register_box_style`. Preloaded styles are

        - ``'ascii-block'``
        - ``'ascii-line'``
        - ``'shaded'``
        - ``'block'``
        - ``'half-block'``
        - ``'half-block-inner'``
        - ``'line'``
        - ``'bold-line'``
        - ``'rounded-line'``
        - ``'double-line'``

        All but the ``'ascii-*'`` styles use unicode characters. The
        default is ``'ascii-block'``.
    alignment : str or None
        A value that indicates how to align lines in multiline strings.
        Acceptable values are as follows:

        ``'left'`` or ``'<'``
            Each string is padded on the right to the length of the
            maximum line length. Shorter lines are left aligned.
        ``'center'`` or ``'^'``
            Each string is padded equally on each side to the length of
            the maximum line length. Shorter lines are center aligned.
        ``'right'`` or ``'>'``
            Each string is padded on the left to the length of the
            maximum line length. Shorter lines are right aligned.

        Default is ``'^'``.
    horizontal_padding : int
        The number of spaces to place between the string and the left
        and right borders. Defaults to one space on each side.
    vertical_padding : int
        The number of newlines to place between the string and the top
        and bottom border. Defaults to one line on each side.
    len_key : callable
        A custom callable for computing the lengths of strings. This can
        be useful for example if the strings contain tabs or some
        similar sequence whose display width is not necessarily the raw
        string width. Defaults to the builtin :py:func:`len`.

    Return
    ------
    box : str
        The input string surrounded by a border box. The return value
        will always be a multi-line string.
    """
    # Get the strings
    vertical_padding = [' '] * vertical_padding
    horizontal_padding  = ' ' * horizontal_padding
    lines = vertical_padding + string.splitlines() + vertical_padding
    lines = split_align(lines, alignment=alignment, width=None,
                        len_key=len_key)
    lines = [horizontal_padding + line + horizontal_padding for line in lines]

    # Get left and right styles, taking into account the corner styles
    style = option_lookup('style', _make_box_styles, style,
                          key_func=str.casefold)

    lwidth = max(_maxlen(style.ul, len_key), _maxlen(style.bl, len_key),
                 _maxlen(style.left, len_key))
    rwidth = max(_maxlen(style.ur, len_key), _maxlen(style.br, len_key),
                 _maxlen(style.right, len_key))
    cwidth = _maxlen(lines, len_key)

    cheight = len(lines)

    ul = split_align(style.ul, alignment='>', width=lwidth, len_key=len_key)
    bl = split_align(style.bl, alignment='>', width=lwidth, len_key=len_key)
    left = split_align(style.left * ceil(cheight / len(style.left)),
                       alignment='>', width=lwidth)
    right = split_align(style.right * ceil(cheight / len(style.right)),
                        alignment='none', width=rwidth)
    top = split_horiz_cat(*([style.top] * ceil(cwidth / _maxlen(style.top))),
                          alignment='<', sep='', linesep=None, missing='down',
                          len_key=len_key)
    top = [line[:cwidth] for line in top]
    top = split_horiz_cat(ul, top, style.ur, sep='', linesep=None,
                          alignment='none', missing='empty', len_key=len_key)
    bottom = split_horiz_cat(
        *([style.bottom] * ceil(cwidth / _maxlen(style.bottom))), sep='',
        alignment='<', linesep=None, missing='empty', len_key=len_key
    )
    bottom = [line[:cwidth] for line in bottom]
    bottom = split_horiz_cat(bl, bottom, style.br, sep='', linesep=None,
                             alignment='none', missing='empty',
                             len_key=len_key)

    lines = split_horiz_cat(left, lines, right, sep='', linesep=None,
                            alignment='none', len_key=len_key)
    lines = top + lines + bottom

    return linesep.join(lines)


def register_box_style(name, top, left, bottom, right, ul, ur, bl, br):
    """
    Create a new box style that is available to :py:func:`make_box`
    through `name`.

    A style is defined by specifying the characters to use for each side
    and corner of the box. Normally, borders are specified as a single
    character, but this is not required.

    Registering an existing style will silently overwrite the previous
    style.

    Parameters
    ----------
    name : str
        The name by which the style will be accessible to
        :py:func:`make_box` via the `style` parameter.
    top : str
        The character or characters to use for the top side of the box.
    left : str
        The character or characters to use for the left side of the box.
    bottom : str
        The character or characters to use for the bottom side of the
        box.
    right : str
        The character or characters to use for the right side of the
        box.
    ul : str
        The character or characters that will join `top` and `left`
        borders in the upper left-hand corner.
    ur : str
        The character or characters that will join `top` and `right`
        borders in the upper right-hand corner.
    bl : str
        The character or characters that will join `bottom` and
        `left` borders in the lower left-hand corner.
    br : str
        The character or characters that will join `bottom` and
        `right` borders in the lower right-hand corner.


    The elements of the left column of the box will be right-aligned
    based on the longest among `ul`, `left` and `bl`. The elements
    of the right side will be similarly left-aligned based on the
    longest among `ur`, `right` and `br`.

    Style string elements may contain multiple lines. In that case, all
    the lines will be left-aligned.
    """
    _make_box_styles[name.casefold()] = _make_box_style(
        top=top.splitlines(), left=left.splitlines(),
        bottom=bottom.splitlines(), right=right.splitlines(),
        ul=ul.splitlines(), ur=ur.splitlines(),
        bl=bl.splitlines(), br=br.splitlines()
    )


register_box_style('ascii-block', *('#' * 8))
register_box_style('ascii-line', *'-|-|', *('+' * 4))

register_box_style('shaded',
    top='\u2593', left='\u2593', bottom='\u2593\n\u2592', right='\u2593\u2592',
    ul='\u2593', ur='\u2593\u2591', bl='\u2593\n\u2591',
    br='\u2593\u2592\n\u2592\u2592')
register_box_style('block', *('\u2588' * 8))
register_box_style('half-block',
    top='\u2580', bottom='\u2584', left='\u258C', right='\u2590',
    ul='\u259B', ur='\u259C', bl='\u2599', br='\u259F')
register_box_style('half-block-inner',
    top='\u2584', bottom='\u2580', left='\u2590', right='\u258C',
    ul='\u2597', ur='\u2596', bl='\u259D', br='\u2598')

register_box_style('line',
    top='\u2500', bottom='\u2500', left='\u2502', right='\u2502',
    ul='\u250C', ur='\u2510', bl='\u2514', br='\u2518')
register_box_style('rounded-line',
    top='\u2500', bottom='\u2500', left='\u2502', right='\u2502',
    ul='\u256D', ur='\u256E', bl='\u2570', br='\u256F')

register_box_style('bold-line',
    top='\u2501', bottom='\u2501', left='\u2503', right='\u2503',
    ul='\u250F', ur='\u2513', bl='\u2517', br='\u251B')
register_box_style('bold-hline',
    top='\u2501', bottom='\u2501', left='\u2502', right='\u2502',
    ul='\u250D', ur='\u2511', bl='\u2515', br='\u2519')
register_box_style('bold-vline',
    top='\u2500', bottom='\u2500', left='\u2503', right='\u2503',
    ul='\u250E', ur='\u2512', bl='\u2516', br='\u251A')
register_box_style('bold-tline',
    top='\u2501', bottom='\u2500', left='\u2502', right='\u2502',
    ul='\u250D', ur='\u2511', bl='\u2514', br='\u2518')
register_box_style('bold-bline',
    top='\u2500', bottom='\u2501', left='\u2502', right='\u2502',
    ul='\u250C', ur='\u2510', bl='\u2515', br='\u2519')
register_box_style('bold-lline',
    top='\u2500', bottom='\u2500', left='\u2503', right='\u2502',
    ul='\u250E', ur='\u2510', bl='\u2516', br='\u2518')
register_box_style('bold-rline',
    top='\u2500', bottom='\u2500', left='\u2502', right='\u2503',
    ul='\u250C', ur='\u2512', bl='\u2514', br='\u251A')

register_box_style('double-line',
    top='\u2550', bottom='\u2550', left='\u2551', right='\u2551',
    ul='\u2554', ur='\u2557', bl='\u255A', br='\u255D')
register_box_style('double-hline',
    top='\u2550', bottom='\u2550', left='\u2502', right='\u2502',
    ul='\u2552', ur='\u2555', bl='\u2558', br='\u255B')
register_box_style('double-vline',
    top='\u2500', bottom='\u2500', left='\u2551', right='\u2551',
    ul='\u2553', ur='\u2556', bl='\u2559', br='\u255C')
register_box_style('double-tline',
    top='\u2550', bottom='\u2500', left='\u2502', right='\u2502',
    ul='\u2552', ur='\u2555', bl='\u2514', br='\u2518')
register_box_style('double-bline',
    top='\u2500', bottom='\u2550', left='\u2502', right='\u2502',
    ul='\u250C', ur='\u2510', bl='\u2558', br='\u255B')
register_box_style('double-lline',
    top='\u2500', bottom='\u2500', left='\u2551', right='\u2502',
    ul='\u2553', ur='\u2510', bl='\u2559', br='\u2518')
register_box_style('double-rline',
    top='\u2500', bottom='\u2500', left='\u2502', right='\u2551',
    ul='\u250C', ur='\u2556', bl='\u2514', br='\u255C')

register_box_style('dashed-line',
    top='\u254C', bottom='\u254C', left='\u254E', right='\u254E',
    ul='\u250C', ur='\u2510', bl='\u2514', br='\u2518')
register_box_style('dash-dotted-line',
    top='\u2504', bottom='\u2504', left='\u2506', right='\u2506',
    ul='\u250C', ur='\u2510', bl='\u2514', br='\u2518')
register_box_style('dotted-line',
    top='\u2508', bottom='\u2508', left='\u250A', right='\u250A',
    ul='\u250C', ur='\u2510', bl='\u2514', br='\u2518')

register_box_style('dashed-bold-line',
    top='\u254D', bottom='\u254D', left='\u254F', right='\u254F',
    ul='\u250F', ur='\u2513', bl='\u2517', br='\u251B')
register_box_style('dash-dotted-bold-line',
    top='\u2505', bottom='\u2505', left='\u2507', right='\u2507',
    ul='\u250F', ur='\u2513', bl='\u2517', br='\u251B')
register_box_style('dotted-bold-line',
    top='\u2509', bottom='\u2509', left='\u250B', right='\u250B',
    ul='\u250F', ur='\u2513', bl='\u2517', br='\u251B')


def check_value(string, options, insensitive=True, label='option'):
    """
    Verifiy that string is within the allowed options.

    Raise a :py:exc:`ValueError` if not found.

    Parameters
    ----------
    string : str
        The string to verify.
    options : mapping[str, str] or iterable[str]
        A container that supports the ``in`` operator. If the container
        is a mapping that can be indexed by the input, the result is
        the "normalized" version of the string that will be returned.
    insensitive : bool
        Whether or not to do a case insensitive comparison (using
        :py:meth:`str.casefold`). If :py:obj:`True`, `options` is
        expected to contain casefolded items.
    label : str
        The label used to describe `string` if it is not found in
        `options`.

    Return
    ------
    check : str
        The input string if it is in `options`. If options is a
        mapping, the result will be ``options[string]`` instead. This
        allows normalization of the input so that multiple input options
        can represent the same output value.
    """
    check = string.casefold() if insensitive else string
    if check not in options:
        raise ValueError('No such {} "{}"'.format(label, string))
    try:
        return options[check]
    except TypeError:
        return check


def to_casefold(string, conv=str):
    """
    Convert the input to a string and casefold it.

    Conversion is done by `conv`, which is normally :py:class:`str`, but
    :py:func:`repr` is sometimes a good choice as well.
    """
    return conv(string).casefold()


def to_lower(string, conv=str):
    """
    Convert the input to a string and lowercase it.

    Conversion is done by `conv`, which is normally :py:class:`str`, but
    :py:func:`repr` is sometimes a good choice as well.
    """
    return conv(string).lower()


def to_upper(string, conv=str):
    """
    Convert the input to a string and uppercase it.

    Conversion is done by `conv`, which is normally :py:class:`str`, but
    :py:func:`repr` is sometimes a good choice as well.
    """
    return conv(string).upper()


def to_hex(b, prefix='', sep=''):
    """
    Convert a string of bytes to a hex string.

    Parameters
    ----------
    b : bytes or bytearray
        The bytes to display.
    prefix : str
        The prefix to prepend to each byte. The default is an empty
        string. Another common choice is ``'0x'``.
    sep : str, optional
        The separator to place between bytes. The default is an empty
        string: hex values are concatenated all together.

    Returns
    -------
    str
        A string consisting of the characters 0-9, A-Z (as well as
        `prefix` and `sep`), with two digits per byte of input.
    """
    return sep.join(f'{x:02X}' for x in b)


def camel2snake(string):
    """
    Convert a string to snake_case, assuming input in CamelCase.

    Parameters
    ----------
    string : str
        The string to convert.

    Returns
    -------
    str
        A string similar to the input, but any uppercase letters are
        lowercased and an underscore is prepended, unless there is one
        there already.
    """
    chars = deque()
    for i, c in enumerate(str(string)):
        if c.isupper():
            if i > 0 and chars[-1] != '_':
                chars.append('_')
            c = c.lower()
        chars.append(c)
    return ''.join(chars)


def snake2camel(string, first_upper=False):
    """
    Convert a string to CamelCase, assuming input in snake_case.

    Parameters
    ----------
    string : str
        The string to convert.
    first_upper : bool
        Whether or not to capitalize the first letter.

    Returns
    -------
    str
        A string similar to the input, but any underscores removed, and
        the following letters uppercased.
    """
    chars = deque()
    next_upper = False
    for c in str(string):
        if c == '_':
            next_upper = True
            continue
        if next_upper:
            c = c.upper()
        chars.append(c)
        next_upper = False
    if first_upper:
        chars[0] = chars[0].upper()
    return ''.join(chars)

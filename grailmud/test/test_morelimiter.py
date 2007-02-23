__copyright__ = """Copyright 2007 Sam Pointon"""

__licence__ = """
This file is part of grailmud.

grailmud is free software; you can redistribute it and/or modify it under the
terms of the GNU General Public License as published by the Free Software
Foundation; either version 2 of the License, or (at your option) any later
version.

grailmud is distributed in the hope that it will be useful, but WITHOUT ANY
WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR
A PARTICULAR PURPOSE.  See the GNU General Public License for more details.

You should have received a copy of the GNU General Public License along with
grailmud (in the file named LICENSE); if not, write to the Free Software
Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA 02110-1301  USA
"""

from grailmud.morelimiter import MoreLimiter
from StringIO import StringIO

def test_basic_more():
    data = "foo\n" * 200
    m = MoreLimiter(10)
    chunks = m.chunk(data)
    for _ in xrange(20):
        res = chunks.next()
        expected = ("foo\n" * 10)
        print repr(expected)
        assert res == expected
    assert chunks.next() == ''

def test_change_limit():
    data = "foo\n" * 200
    m = MoreLimiter(1)
    m.change_limit(10)
    chunks = m.chunk(data)
    for _ in xrange(20):
        res = chunks.next()
        expected = ("foo\n" * 10)
        print  repr(expected)
        assert res == expected
    assert chunks.next() == ''

def test_shorter_than_capacity():
    data = "foo"
    m = MoreLimiter(10)
    chunks = m.chunk(data)
    assert chunks.next() == data

def test_clearfeed_raise():
    data = "foo"
    m = MoreLimiter(10)
    chunks = m.chunk(data)
    assert chunks.next() == data
    try:
        chunks.next()
    except StopIteration:
        pass
    else:
        assert False

def test_multiple_chunkage():
    data = "foo"
    m = MoreLimiter(10)
    m.chunk("bar")
    chunks = m.chunk(data)
    assert chunks.next() == data

def test_empty_then_chunk():
    data = "foo"
    m = MoreLimiter(10)
    chunks = m.chunk(data)
    assert chunks.next() == data
    data = "bar"
    chunks = m.chunk(data)
    assert chunks.next() == data

def test_empty_error_then_chunk():
    data = "foo"
    m = MoreLimiter(10)
    chunks = m.chunk(data)
    assert chunks.next() == data
    try:
        chunks.next()
    except StopIteration:
        pass
    else:
        assert False
    data = "bar"
    chunks = m.chunk(data)
    assert chunks.next() == data

def test_change_limit_then_chunk():
    data = "foo\n" * 200
    m = MoreLimiter(1)
    chunks = m.chunk(data)
    m.change_limit(10)
    for _ in xrange(20):
        assert chunks.next() == ("foo\n" * 10)

def test_reported_length():
    data = "foo\n" * 499
    m = MoreLimiter(10)
    chunks = m.chunk(data)
    assert chunks.initial_lines == 500 #plus the emptiness at the end.
    assert chunks.next() == ("foo\n" * 10)
    assert chunks.lines_left == 490
    m.change_limit(5)
    assert chunks.initial_lines == 500
    assert chunks.next() == ("foo\n" * 5)
    assert chunks.lines_left == 485

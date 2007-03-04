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

from grailmud.nvt import make_string_sane

def test_removal_of_NUL():
    s = '\000foo\000bar'
    assert make_string_sane(s) == 'foobar'

def test_removal_of_BEL():
    s = '\007James\007 Bond'
    assert make_string_sane(s) == 'James Bond'

def test_backspace_handling_normal():
    s = 'fooX\010'
    res = make_string_sane(s)
    print res
    assert res == 'foo'

def test_backspace_handling_multiple():
    s = 'fooXXX\010\010\010bar'
    res = make_string_sane(s)
    print res
    assert res == 'foobar'

def test_backspace_handling_no_previous_characters_no_blow_up():
    s = '\010'
    assert make_string_sane(s) == ''

def test_backspace_no_interference():
    s = 'fooX\000\010'
    res = make_string_sane(s)
    print res
    assert res == 'foo'

def test_HT_removal():
    s = 'foo\011bar'
    assert make_string_sane(s) == 'foobar'

def test_VT_removal():
    s = 'foo\013\013bar'
    assert make_string_sane(s) == 'foobar'

def test_FF_removal():
    s = 'foo\014bar'
    assert make_string_sane(s) == 'foobar'

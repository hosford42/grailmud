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

from grailmud.strutils import *

class Testsafetise(object):

    def test_iac_removal(self):
        text = 'foo\xffbar'
        assert self.func(text) == 'foobar'

    func = staticmethod(safetise)

class Testsanitise(Testsafetise):

    def test_number_removal(self):
        text = 'foo23bar'
        assert self.func(text) == 'foobar'

    def test_punctuation_removal(self):
        text = 'foo,:?bar'
        assert self.func(text) == 'foobar'

    func = staticmethod(sanitise)

class Testalphatise(Testsanitise):

    def test_space_removal(self):
        text = '\n foo\tbar\n'
        assert self.func(text) == 'foobar'

    func = staticmethod(alphatise)


def test_head_word_split_single_alpha():
    text = 'foo'
    res = head_word_split(text)
    print res
    assert res == ('foo', '')

def test_head_word_split_multi_alpha():
    text = 'foo bar'
    res = head_word_split(text)
    print res
    assert res == ('foo', 'bar')

def test_head_word_split_leading_whitespace():
    text = ' foo bar'
    res = head_word_split(text)
    print res
    assert res == ('foo', 'bar')

def test_head_word_split_multi_alpha_extra_whitespace():
    text = 'foo     bar'
    res = head_word_split(text)
    print res
    assert res == ('foo', 'bar')

def test_head_word_split_preseve_space():
    text = 'foo   bar \nbaz'
    res = head_word_split(text)
    print repr(res)
    assert res == ('foo', 'bar \nbaz')

def test_head_word_split_single_punct():
    text = '?!'
    assert head_word_split(text) == ('?!', '')

def test_head_word_split_multi_punct_together():
    text = '?foo'
    res = head_word_split(text)
    print res
    assert res == ('?', 'foo')

def test_head_word_split_all_space():
    text = '    \n\t   '
    res = head_word_split(text)
    print res
    assert res == ('', '')

def test_wsnormalise_no_space():
    text = 'foobarbaz'
    res = wsnormalise(text)
    print res
    assert res == text

def test_wsnormalise_normalised_space():
    text = 'foo bar baz'
    res = wsnormalise(text)
    print res
    assert res == text

def test_wsnormalise_leading_whitespace():
    text = ' foo'
    res = wsnormalise(text)
    print res
    assert res == 'foo'

def test_wsnormalise_trailing_whitespace():
    text = 'foo '
    res = wsnormalise(text)
    print res
    assert res == 'foo'

def test_wsnormalise_bad_whitespace():
    text = 'foo  bar    \t baz\n'
    res = wsnormalise(text)
    print repr(res)
    assert res == 'foo bar baz'

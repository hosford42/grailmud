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

from grailmud.actiondefs.core import UnfoundActionEvent, unfoundAction, \
                                     register, shorttarget_pattern, \
                                     adjs_pattern, object_pattern
from grailmud.utils_for_testing import SetupHelper
from collections import defaultdict
from grailmud.objects import MUDObject
from nose.tools import raises
from pyparsing import ParseException, StringEnd, Suppress, Word
from string import printable

def test_registered_default_factory():
    d = defaultdict()
    register(d)
    assert d.default_factory() is unfoundAction

class TestunfoundAction(SetupHelper):

    def setUp(self):
        self.obj = MUDObject(None)
        self.setup_for_object(self.obj)

    def test_receive_event(self):
        unfoundAction(self.obj, '', None)
        assert self.obj.listener.received == [UnfoundActionEvent()]

class Testshorttarget_pattern(object):

    pattern = shorttarget_pattern

    def test_good(self):
        res = list(self.pattern.parseString("$foo")[0])
        print locals()
        assert res == ["foo"]

    @raises(ParseException)
    def test_extra_bits_at_end(self):
        #this may look like cheating, but it's not. It makes sure that 
        #shorttarget_pattern doesn't sneakily eat everything up to the very end
        #of the string, even when that would be Bad.
        strict = self.pattern + StringEnd()
        print strict.parseString("$foo bar")

    @raises(ParseException)
    def test_no_dollar(self):
        print self.pattern.parseString("foo")

    @raises(ParseException)
    def test_extra_at_beginning(self):
        #see note above, but this is really for object_pattern's tests below.
        pat = self.pattern + StringEnd()
        print self.pattern.parseString("bar $foo")
        
    @raises(ParseException)
    def test_empty(self):
        print self.pattern.parseString("")

    def test_with_real_pattern(self):
        pat = self.pattern + Suppress(',') + Word(printable)
        res = list(pat.parseString('$foo, bar'))
        res[0] = list(res[0])
        print res
        assert res == [['foo'], 'bar']

class Testadjs_pattern(object):

    pattern = adjs_pattern

    def test_good_no_number(self):
        res = self.pattern.parseString("foo bar")[0]
        assert len(res) == 2
        res = [list(res[0]), res[1]]
        print res
        assert res == [["foo", "bar"], "0"]

    def test_good_with_number(self):
        res = self.pattern.parseString("foo bar 42")[0]
        assert len(res) == 2
        res = [list(res[0]), res[1]]
        print res
        assert res == [["foo", "bar"], "42"]

    @raises(ParseException)
    def test_empty(self):
        print self.pattern.parseString("")

class Testobject_pattern(Testadjs_pattern, Testshorttarget_pattern):

    pattern = object_pattern
    
    def test_no_dollar(self):
        #this becomes valid, so we disable the test.
        pass

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

from grailmud.utils_for_testing import SetupHelper
from grailmud.actiondefs.setting import LDescSetEvent, setDistribute, setLDesc, \
                                      register, syntax_message
from grailmud.objects import TargettableObject
from grailmud.actiondefs.system import BadSyntaxEvent

def test_registration():
    cdict = {}
    register(cdict)
    assert cdict['set'] is setDistribute

def test_default_ldesc():
    assert TargettableObject("a fat elf", set(), None).ldesc == \
           "a fat elf. Nothing more, nothing less."

def test_ldesc_setting():
    obj = TargettableObject("a fat elf", set(), None)
    desc = "A really really fat elf."
    setLDesc(obj, desc)
    assert obj.ldesc == desc

class TestEvents(SetupHelper):

    def setUp(self):
        self.obj = TargettableObject("a fat elf", set(), None)
        self.setup_for_object(self.obj)

    def test_ldesc_event(self):
        desc = "foo bar"
        setLDesc(self.obj, desc)
        assert self.obj.listener.received == [LDescSetEvent(desc)]

    def test_parsing_ldesc(self):
        desc = "foo bar"
        setDistribute(self.obj, "ldesc %s" % desc, None)
        print self.obj.listener.received
        assert self.obj.listener.received == [LDescSetEvent(desc)]

    def test_bad_syntaxes(self):
        for evilbad in ["foo", "bar baz", "quuux"]:
            setDistribute(self.obj, evilbad, None)
            print self.obj.listener.received
            assert self.obj.listener.received == \
                                     [BadSyntaxEvent(syntax_message % evilbad)]
            self.obj.listener.received = []
            
    def test_parsing_ldesc_ignores_leading_spaces(self):
        desc = '    foo bar'
        setDistribute(self.obj, 'ldesc %s' % desc, None)
        assert self.obj.listener.received == [LDescSetEvent('foo bar')]
        assert self.obj.ldesc == 'foo bar'

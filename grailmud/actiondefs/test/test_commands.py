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

from grailmud.actiondefs.commands import invert_dict

def test_invert_dict_single_valued():
    d = {'foo': 'bar',
         'baz': 'qux'}
    res = invert_dict(d)
    assert res == {'bar': set(['foo']), 'qux': set(['baz'])}

def test_invert_dict_multi_valued():
    d = {'foo': 'bar',
         'baz': 'bar'}
    res = invert_dict(d)
    assert res == {'bar': set(['foo', 'baz'])}

from grailmud.actiondefs.commands import CommandListEvent, NoCommandListEvent
from grailmud.events import SystemEvent

def test_CommandListEvent_is_a_SystemEvent():
    assert issubclass(CommandListEvent, SystemEvent)

def test_NoCommandListEvent_is_a_SystemEvent():
    assert issubclass(NoCommandListEvent, SystemEvent)

def test_CommandListEvent_store_command_list_instance_variable():
    sentinel = object()
    ev = CommandListEvent(sentinel)
    assert ev.command_list is sentinel

from grailmud.objects import MUDObject

class MockObjectWithCommands(MUDObject):

    cmdict = {'foo': 'bar', 'baz': 'bar', 'qux': 'spam'}

from grailmud.utils_for_testing import SetupHelper
from grailmud.actiondefs.commands import list_commands

class TestEventSending(SetupHelper):

    expected = [set(['foo', 'baz']), set(['qux'])]

    def setUp(self):
        self.obj = MockObjectWithCommands(None)
        self.setup_for_object(self.obj)
        self.failobj = MUDObject(None)
        self.setup_for_object(self.failobj)

    def test_event_sending_success(self):
        list_commands(self.obj)
        assert self.obj.delegate.received == [CommandListEvent(self.expected)]

    def test_event_sending_no_cmd_list(self):
        list_commands(self.failobj)
        assert self.failobj.delegate.received == [NoCommandListEvent()]

    def test_wrapper_success(self):
        d = {}
        register(d)
        d['commands'](self.obj, '', None)
        assert self.obj.delegate.received == [CommandListEvent(self.expected)]


from grailmud.actiondefs.commands import register

def test_register():
    d = {}
    register(d)
    #anonymous wrapper
    assert d['commands']


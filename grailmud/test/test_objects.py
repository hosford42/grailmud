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

from grailmud.objects import MUDObject, TargettableObject, NamedObject, \
                             Player, TargettableExitObject
from grailmud.events import BaseEvent
import pickle
from grailmud.utils_for_testing import MockListener as ListenerHelper, \
        SetupHelper

#XXX: I would -love- to have some proper tests for pickling here, but 
#unfortunately, due to the design of the system, it's not really an option. And
#the design of the system wasn't really an option either. Ho-hum...

def test_at_least_calls_the_base___Xstate__():
    obj = MUDObject(None)
    s = pickle.dumps(obj)
    try:
        o = pickle.loads(s)
    except RuntimeError:
        #well, we called it...
        pass
    else:
        assert False, "got %r instead" % o

def test_register():
    obj = MUDObject(None)
    obj.addListener(ListenerHelper(obj))

def test_equality():
    m = MUDObject(None)
    assert m == m
    assert MUDObject(None) != m

def test_hashability():
    s = set([MUDObject(None), MUDObject(None)])
    assert len(s) == 2

class TesterForListening(object):

    def setUp(self):
        self.obj = MUDObject(None)
        self.obj.addListener(ListenerHelper(self.obj))
        
    def test_unregister(self):
        self.obj.removeListener(self.obj.listener)

    def test_event_passing(self):
        self.obj.receiveEvent(BaseEvent())
        assert self.obj.listener.received == [BaseEvent()]

    def test_event_flushing(self):
        self.obj.eventFlush()
        assert self.obj.listener.flushed

    def test_bad_unregister(self):
        self.obj.listeners.remove(self.obj.listener)
        try:
            self.obj.removeListener(self.obj.listener)
        except ValueError:
            pass
        else:
            assert False

    def test_bad_register(self):
        try:
            self.obj.addListener(self.obj.listener)
        except ValueError:
            pass
        else:
            assert False

def test_caseless_naming_in_adjs():
    obj = NamedObject('', 'FOO', set(), None)
    assert obj.adjs == set(['foo'])
    NamedObject._name_registry.clear()

def test_caseless_addition_to_name_registry():
    obj = NamedObject('', 'FOO', set(), None)
    assert 'FOO' not in NamedObject._name_registry
    assert NamedObject._name_registry['foo'] is obj
    NamedObject._name_registry.clear()

def test_TargettableExitObject_matching():
    obj = TargettableExitObject(None, None, '', set(['foo']))
    assert obj.match(set(['foo']))

class Test_receivedLine(SetupHelper):

    def setUp(self):
        self.issued = []
        self.obj = Player('foo', '', set(), None,
                          '')
        self.obj.cmdict = {'foo': self.record_command}

    def tearDown(self):
        del NamedObject._name_registry[self.obj.name]

    def record_command(self, actor, text, info):
        self.issued.append((actor, text, info))

    def test_no_rest_of_line(self):
        sentinelinfo = object()
        self.obj.receivedLine('foo', sentinelinfo)
        assert self.issued == [(self.obj, '', sentinelinfo)]

    def test_rest_of_line(self):
        sentinelinfo = object()
        self.obj.receivedLine('foo bar', sentinelinfo)
        assert self.issued == [(self.obj, 'bar', sentinelinfo)]

    def test_caseless_command(self):
        sentinelinfo = object()
        self.obj.receivedLine('FOO bar', sentinelinfo)
        assert self.issued == [(self.obj, 'bar', sentinelinfo)]



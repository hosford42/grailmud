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

from grailmud.actiondefs.look import LookAtEvent, LookRoomEvent, lookDistributor,\
                                   lookAt, lookRoom, register
from grailmud.utils_for_testing import SetupHelper
from grailmud.objects import TargettableObject, TargettableExitObject, NamedObject, \
                           MUDObject
from grailmud.rooms import Room
from grailmud.actiondefs.system import UnfoundObjectEvent

def test_registration():
    d = {}
    register(d)
    assert d['l'] is lookDistributor
    assert d['look'] is lookDistributor

class MockInfo(object):

    def __init__(self, instigator):
        self.instigator = instigator

class TestEventSending(SetupHelper):

    def setUp(self):
        self.room = Room("Just outside a dark cave.", "")
        self.actor = TargettableObject("a decapitated knight",
                                       set(['shiny', 'dead']),
                                       self.room)
        self.roomtarget = TargettableObject("a killer rabbit",
                                            set(['bunny', 'fluffy', "rabbit",
                                                 'murderous', "killer"]),
                                            self.room)
        self.invtarget = NamedObject("a surprised-looking decapitated head",
                                     "Boris", set(["head", "dead"]),
                                     self.actor.inventory)
        self.otherroom = Room("Just inside a dark cave.", "")
        self.exit = TargettableExitObject(self.room, self.otherroom,
                                          "the mouth of a cave", 
                                          set(["cave", "mouth"]))

        self.room.add(self.actor)
        self.room.add(self.roomtarget)
        self.room.add(self.invtarget)
        self.room.add(self.exit)

        self.setup_for_object(self.actor)

        self.info = MockInfo(self.actor)

    def tearDown(self):
        self.room.remove_from_instances()
        self.actor.remove_from_instances()
        self.roomtarget.remove_from_instances()
        self.invtarget.remove_from_instances()
        NamedObject._name_registry.clear()
        self.exit.remove_from_instances()

    def test_look_at_room_TargettableObject(self):
        lookAt(self.actor, self.roomtarget)

        assert self.actor.listener.received == [LookAtEvent(self.roomtarget)]

    def test_look_at_inventory_TargettableObject(self):
        lookAt(self.actor, self.invtarget)

        assert self.actor.listener.received == [LookAtEvent(self.invtarget)]
        
    def test_look_at_nowhere(self):
        lookAt(self.actor, MUDObject(None))

        assert self.actor.listener.received == [UnfoundObjectEvent()]

    def test_look_at_room(self):
        lookRoom(self.actor)

        assert self.actor.listener.received == [LookRoomEvent(self.room)]

    def test_look_at_exit(self):
        lookAt(self.actor, self.exit)

        assert self.actor.listener.received == [LookRoomEvent(self.otherroom)]

    def test_look_at_parsing_no_at(self):
        lookDistributor(self.actor, 'boris', self.info)

        print self.actor.listener.received
        assert self.actor.listener.received == [LookAtEvent(self.invtarget)]

    def test_look_at_parsing(self):
        lookDistributor(self.actor, "at killer rabbit", self.info)

        print self.actor.listener.received
        assert self.actor.listener.received == [LookAtEvent(self.roomtarget)]

    def test_look_at_parsing_failure(self):
        lookDistributor(self.actor, "at foobar", self.info)

        assert self.actor.listener.received == [UnfoundObjectEvent()]

    def test_look_parsing(self):
        lookDistributor(self.actor, "", self.info)

        print self.actor.listener.received
        assert self.actor.listener.received == [LookRoomEvent(self.room)]
    

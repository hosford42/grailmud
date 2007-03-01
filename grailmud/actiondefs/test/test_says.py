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

from grailmud.actiondefs.says import SpeakNormalFirstEvent, \
        SpeakNormalThirdEvent, SpeakToFirstEvent, SpeakToSecondEvent, \
        SpeakToThirdEvent, speakToWrapper, speak, speakTo, register
from grailmud.events import AudibleEvent
from grailmud.utils_for_testing import SetupHelper

def test_register():
    d = {}
    register(d)
    #a wrapper's used, so we can't test for identity. Just check presence and
    #equivalency
    assert d['"'] == d["'"] == d['say']
    #these have a defined wrapper, though
    assert speakToWrapper is d["',"] is d['",'] is d['say,'] is d['sayto']

def test_all_events_are_AudibleEvents():
    for cls in [SpeakNormalFirstEvent, SpeakNormalThirdEvent, 
                SpeakToFirstEvent, SpeakToSecondEvent, SpeakToThirdEvent]:
        print cls
        assert issubclass(cls, AudibleEvent)

from grailmud.objects import MUDObject, TargettableObject
from grailmud.rooms import AnonyRoom
from grailmud.actiondefs.system import UnfoundObjectEvent

class TestEventSending(SetupHelper):

    def setUp(self):
        self.room = AnonyRoom()
        self.actor = MUDObject(self.room)
        self.target = TargettableObject("", set('rabbit'), self.room)
        self.onlooker = MUDObject(self.room)
        self.other_room_target = TargettableObject('', set(), None)
        self.setup_for_object(self.actor)
        self.setup_for_object(self.target)
        self.setup_for_object(self.onlooker)

    def test_speak_actor_receives_event(self):
        speak(self.actor, "foo")
        assert self.actor.listener.received == [SpeakNormalFirstEvent("foo")]

    def test_speak_room_receives_event(self):
        speak(self.actor, "foo")
        assert self.target.listener.received == \
                                  [SpeakNormalThirdEvent(self.actor, "foo")]

    def test_speakTo_actor_receives_event(self):
        speakTo(self.actor, self.target, "foo")
        assert self.actor.listener.received == [SpeakToFirstEvent(self.target,
                                                                  "foo")]

    def test_speakTo_target_receives_event(self):
        speakTo(self.actor, self.target, "foo")
        print self.target.listener.received
        assert self.target.listener.received == [SpeakToSecondEvent(self.actor,
                                                                    "foo")]

    def test_speakTo_room_receives_event(self):
        speakTo(self.actor, self.target, "foo")
        assert self.onlooker.listener.received == \
                          [SpeakToThirdEvent(self.actor, self.target, "foo")]

    def test_speakTo_fails_with_nonTargettableObject(self):
        speakTo(self.actor, MUDObject(None), "foo")
        assert self.actor.listener.received == [UnfoundObjectEvent()]

    def test_speakTo_fails_target_out_of_room(self):
        speakTo(self.actor, self.other_room_target, "foo")
        assert self.actor.listener.received == [UnfoundObjectEvent()]

    #XXX: test parsing

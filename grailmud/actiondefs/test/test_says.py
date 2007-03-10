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
        SpeakToThirdEvent, speakToWrapper, speak, speakTo, register, \
        speakToPattern
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
from grailmud.telnet import LineInfo
from grailmud.actiondefs.system import BadSyntaxEvent
from grailmud.actiondefs.targetting import targetSet

class TestEventSending(SetupHelper):

    def setUp(self):
        self.room = AnonyRoom()
        self.actor = MUDObject(self.room)
        self.target = TargettableObject("", set(['rabbit']), self.room)
        self.onlooker = MUDObject(self.room)
        self.other_room_target = TargettableObject('', set(), None)
        self.setup_for_object(self.actor)
        self.setup_for_object(self.target)
        self.setup_for_object(self.onlooker)
        self.info = LineInfo(instigator = self.actor)

    def test_speak_actor_receives_event(self):
        speak(self.actor, "foo")
        assert self.actor.delegate.received == [SpeakNormalFirstEvent("foo")]

    def test_speak_room_receives_event(self):
        speak(self.actor, "foo")
        assert self.target.delegate.received == \
                                  [SpeakNormalThirdEvent(self.actor, "foo")]

    def test_speakTo_actor_receives_event(self):
        speakTo(self.actor, self.target, "foo")
        assert self.actor.delegate.received == [SpeakToFirstEvent(self.target,
                                                                  "foo")]

    def test_speakTo_target_receives_event(self):
        speakTo(self.actor, self.target, "foo")
        print self.target.delegate.received
        assert self.target.delegate.received == [SpeakToSecondEvent(self.actor,
                                                                    "foo")]

    def test_speakTo_room_receives_event(self):
        speakTo(self.actor, self.target, "foo")
        assert self.onlooker.delegate.received == \
                          [SpeakToThirdEvent(self.actor, self.target, "foo")]

    def test_speakTo_fails_with_nonTargettableObject(self):
        speakTo(self.actor, MUDObject(None), "foo")
        assert self.actor.delegate.received == [UnfoundObjectEvent()]

    def test_speakTo_fails_target_out_of_room(self):
        speakTo(self.actor, self.other_room_target, "foo")
        assert self.actor.delegate.received == [UnfoundObjectEvent()]

    def test_speakToWrapper_success(self):
        speakToWrapper(self.actor, "rabbit, foo", self.info)
        print self.actor.delegate.received[0].__dict__
        assert self.actor.delegate.received == [SpeakToFirstEvent(self.target,
                                                                  "foo")]

    def test_speakToWrapper_success_multiword(self):
        speakToWrapper(self.actor, "rabbit, foo bar", self.info)
        print self.actor.delegate.received
        print self.actor.delegate.received[0].__dict__
        assert self.actor.delegate.received == [SpeakToFirstEvent(self.target,
                                                                  "foo bar")]

    def test_speakToWrapper_parsing_failure(self):
        speakToWrapper(self.actor, "bogusinputomatic", self.info)
        assert self.actor.delegate.received == [BadSyntaxEvent(None)]

    def test_speakToWrapper_finding_target_failure(self):
        speakToWrapper(self.actor, "bogus target, foo", self.info)
        assert self.actor.delegate.received == [UnfoundObjectEvent()]

    def test_speakToWrapper_with_target(self):
        targetSet(self.actor, "foo", self.target)
        self.actor.delegate.received = []
        speakToWrapper(self.actor, "$foo, bar", self.info)
        res = self.actor.delegate.received
        print res
        assert res == [SpeakToFirstEvent(self.target, "bar")]

def test_speakToPattern_with_target():
    res = list(speakToPattern.parseString('$foo, bar'))
    res[0] = list(res[0])
    print res
    assert res == [['foo'], 'bar']

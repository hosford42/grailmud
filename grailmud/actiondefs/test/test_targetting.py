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

from grailmud.actiondefs.targetting import register, TargetSetEvent, TargetClearedEvent, TargetAlreadyClearedEvent, TargetListEvent, target_set_pattern, target_clear_pattern, target_list_pattern, targetDistributor, targetSet, targetList, targetClear
from grailmud.objects import MUDObject, TargettableObject
from grailmud.actiondefs.system import BadSyntaxEvent
from grailmud.events import BaseEvent
from pyparsing import ParseException
from grailmud.utils_for_testing import SetupHelper
from grailmud.rooms import AnonyRoom
from nose.tools import raises
from grailmud.actiondefs.system import UnfoundObjectEvent

def test_registering():
    d = {}
    register(d)
    assert d['target'] is targetDistributor

def test_events_are_subclasses_of_BaseEvent():
    for cls in [TargetSetEvent, TargetClearedEvent, TargetAlreadyClearedEvent, TargetListEvent]:
        assert issubclass(cls, BaseEvent)

class Testtarget_set_pattern(object):

    def test_doesnt_blow_up_on_good_input(self):
        print target_set_pattern.parseString("set $foo to bar baz")

    @raises(ParseException)
    def test_blows_up_on_missing_dollar(self):
        print target_set_pattern.parseString("set foo to bar")

    def test_two_names_captured(self):
        res = target_set_pattern.parseString("set $foo to bar baz")
        print res
        assert len(res)== 2

class Testtarget_clear_pattern(object):

    def test_doesnt_blow_up_on_good_input(self):
        target_clear_pattern.parseString("clear $foo")

    @raises(ParseException)
    def test_blows_up_on_missing_dollar(self):
        target_clear_pattern.parseString("clear foo")

    def test_one_name_captured(self):
        assert len(target_clear_pattern.parseString("clear $foo")) == 1

class Testtarget_list_pattern(object):

    def test_doesnt_blow_up_on_good_input(self):
        target_list_pattern.parseString("list")

    def test_no_capture(self):
        assert not len(target_list_pattern.parseString("list"))

def test_default_targetting_shorts():
    assert MUDObject(None).targetting_shorts == {}

class MockInfo(object):

    def __init__(self, instigator):
        self.instigator = instigator

class TestActualEvents(SetupHelper):

    def setUp(self):
        self.room = AnonyRoom()
        self.actor = MUDObject(self.room)
        self.target = TargettableObject("a killer rabbit", set(['bunny',
                                                                'killer',
                                                                'rabbit']),
                                        self.room)
        self.setup_for_object(self.actor)
        self.setup_for_object(self.target)
        self.info = MockInfo(self.actor)

    def test_targetSet(self):
        targetSet(self.actor, 'robert', self.target)
        assert self.actor.targetting_shorts['robert'] is self.target


    def test_targetSet_messages(self):
        targetSet(self.actor, "robert", self.target)
        assert self.actor.listener.received == [TargetSetEvent("robert",
                                                               self.target)]

    def test_targetClear_success(self):
        self.actor.targetting_shorts['bob'] = self.target
        targetClear(self.actor, 'bob')
        assert 'bob' not in self.actor.targetting_shorts

    def test_targetClear_success_messages(self):
        self.actor.targetting_shorts['bob'] = self.target
        targetClear(self.actor, 'bob')
        assert self.actor.listener.received == [TargetClearedEvent("bob")]

    def test_targetClear_fail(self):
        targetClear(self.actor, "mike")
        assert 'mike' not in self.actor.targetting_shorts

    def test_targetClear_messages(self):
        targetClear(self.actor, "mike")
        assert self.actor.listener.received == \
                                          [TargetAlreadyClearedEvent('mike')]

    def test_targetList_messages(self):
        targetList(self.actor)
        assert self.actor.listener.received == [TargetListEvent(self.actor)]

    def test_targetSet_parsing(self):
        targetDistributor(self.actor, "set $mike to killer rabbit", self.info)
        assert self.actor.listener.received == [TargetSetEvent("mike",
                                                               self.target)]

    def test_targetSet_parsing_failure(self):
        targetDistributor(self.actor, "set $mike to bogus object", self.info)
        assert self.actor.listener.received == [UnfoundObjectEvent()]

    def test_targetSet_caseless(self):
        targetDistributor(self.actor, "set $ROBERT to rabbit", self.info)
        assert self.actor.targetting_shorts['robert'] is self.target

    def test_targetClear_parsing(self):
        self.actor.targetting_shorts['bob'] = self.target
        targetDistributor(self.actor, "clear $bob", self.info)
        print self.actor.listener.received
        assert self.actor.listener.received == [TargetClearedEvent("bob")]

    def test_targetClear_parsing_caseless(self):
        self.actor.targetting_shorts['bob'] = self.target
        targetDistributor(self.actor, "clear $BOB", self.info)
        print self.actor.listener.received
        assert self.actor.listener.received == [TargetClearedEvent("bob")]

    def test_bogus_syntax(self):
        targetDistributor(self.actor, "bogus syntax", self.info)
        assert self.actor.listener.received == [BadSyntaxEvent(None)]

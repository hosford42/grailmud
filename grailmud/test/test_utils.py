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

from grailmud.utils import InstanceTracker
import pickle

class FooClass(InstanceTracker):
    pass

def _helper(constructor, cls = None):
    cls = constructor if cls is None else cls

    assert isinstance(constructor(), InstanceTracker)
    
    i = constructor()
    assert i in cls._instances
    i2 = constructor()
    assert i2 in cls._instances

    i.remove_from_instances()
    assert i not in cls._instances

def test_basics_no_subclassing():
    _helper(FooClass)

class FooSubclass(FooClass):
    pass

def test_non_instance_tracking_subclass():
    assert "_instances" in FooSubclass.__dict__

def test_superclass_tracking():
    _helper(FooSubclass, FooClass)
    _helper(FooSubclass)

def test_non_equality():
    assert FooClass() != FooClass()

def test_equality():
    obj = FooClass()
    assert obj == obj

def test_pickling_throwing_error():
    obj = FooClass()
    objdump = pickle.dumps(obj)
    FooClass()
    print FooClass.__setstate__
    try:
        newobj = pickle.loads(objdump)
    except RuntimeError:
        pass
    else:
        assert newobj is obj

from grailmud.utils import defaultinstancevariable

class BlankClass():
    pass

def test_raises_AttributeError_with_no_instance():
    @defaultinstancevariable(BlankClass, "foo")
    def nonereturner(self):
        return None
    try:
        print BlankClass.foo
    except AttributeError:
        pass
    else:
        assert False

def test_not_called_if_in_dict():
    @defaultinstancevariable(BlankClass, "foo")
    def nonereturner(self):
        called.append(True)
    called = []
    b = BlankClass()
    b.foo = "bar"
    assert b.foo == "bar"
    assert not called

def test_called_if_not_in_dict():
    sentinel = object()
    @defaultinstancevariable(BlankClass, "foo")
    def sentinelreturner(self):
        return sentinel
    b = BlankClass()
    assert b.foo is sentinel

class BlankSubclass(BlankClass):
    pass

def test_default_inheriting():
    sentinel = object()
    @defaultinstancevariable(BlankClass, "foo")
    def sentinelreturner(self):
        return sentinel
    b = BlankSubclass()
    assert b.foo is sentinel

from grailmud.utils import smartdict

def test_smartdict_expr_evaluation():
    res = ("%('foo'.upper())s" % smartdict())
    print res
    assert res == "FOO"

def test_smartdict_variable_namespace():
    res = ("%(foo.lower())s" % smartdict(foo = 'FOO'))
    print res
    assert res == "foo"


from grailmud.utils import get_from_rooms
from grailmud.rooms import UnfoundError, AnonyRoom
from grailmud.actiondefs.core import shorttarget_pattern, object_pattern, \
                                     adjs_pattern
from grailmud.objects import TargettableObject, MUDObject
from grailmud.utils_for_testing import SetupHelper
from grailmud.actiondefs.targetting import targetSet

class LineInfoMockup(object):

    def __init__(self, instigator):
        self.instigator = instigator

class TestGetterFromRooms(SetupHelper):

    def setUp(self):
        self.room = AnonyRoom()
        self.target = TargettableObject("a killer rabbit", 
                                        set(['killer', 'rabbit', 'bunny', 
                                             'fluffy']), 
                                        self.room)
        self.setup_for_object(self.target)
        self.actor = MUDObject(self.room)
        self.setup_for_object(self.actor)
        targetSet(self.actor, "bob", self.target)
        self.info = LineInfoMockup(self.actor)
        self.bogusroom = AnonyRoom()

    def test_shorttarget_success(self):
        parseres = shorttarget_pattern.parseString("$bob")[0]
        res = get_from_rooms(parseres, [self.room], self.info)
        assert res is self.target

    def test_shorttarget_failure(self):
        parseres = shorttarget_pattern.parseString("$mike")[0]
        try:
            print get_from_rooms(parseres, [self.room], self.info)
        except UnfoundError:
            pass
        else:
            assert False

    def test_shorttarget_caseless(self):
        parseres = shorttarget_pattern.parseString("$BOB")[0]
        res = get_from_rooms(parseres, [self.room], self.info)
        assert res is self.target

    def test_adjs_no_number_success(self):
        parseres = adjs_pattern.parseString("killer rabbit")[0]
        res = get_from_rooms(parseres, [self.room], self.info)
        assert res is self.target

    def test_adjs_numbered_success(self):
        parseres = adjs_pattern.parseString("killer rabbit 0")[0]
        res = get_from_rooms(parseres, [self.room], self.info)
        assert res is self.target

    def test_adjs_no_number_failure(self):
        parseres = adjs_pattern.parseString("harmless gopher")[0]
        try:
            print get_from_rooms(parseres, [self.room], self.info)
        except UnfoundError:
            pass
        else:
            assert False

    def test_adjs_number_failure(self):
        parseres = adjs_pattern.parseString("killer rabbit 42")[0]
        try:
            print get_from_rooms(parseres, [self.room], self.info)
        except UnfoundError:
            pass
        else:
            assert False

    def test_adjs_caseless(self):
        parseres = adjs_pattern.parseString("KILLER RABBIT")[0]
        res = get_from_rooms(parseres, [self.room], self.info)
        assert res is self.target

    def test_not_in_very_first_room(self):
        parseres = adjs_pattern.parseString("KILLER RABBIT")[0]
        res = get_from_rooms(parseres, [self.bogusroom, self.room], self.info)
        assert res is self.target

from grailmud.utils import Matcher
from pyparsing import ParseException

def test_Matcher_passes_same_argument_to_matches():
    class DummyPyparsingThingy:
        def parseString(self, obj):
            assert obj is sentinel
    sentinel = object()
    m = Matcher(sentinel)
    m.match(DummyPyparsingThingy())

def test_Matcher_match_returns_True_when_no_raise():
    class DummyPyparsingThingy:
        def parseString(self, obj):
            pass
    m = Matcher("foo")
    assert m.match(DummyPyparsingThingy())

def test_Matcher_match_sets_result_on_success():
    sentinel = object()
    class DummyPyparsingThingy:
        def parseString(self, obj):
            return sentinel
    m = Matcher("foo")
    m.match(DummyPyparsingThingy())
    assert m.results is sentinel

def test_Matcher_results_is_None_default():
    assert Matcher('').results is None

def test_Matcher_match_returns_False_on_ParseException():
    class DummyPyparsingThingy:
        def parseString(self, obj):
            raise ParseException(None, None, None)
    m = Matcher("foo")
    assert not m.match(DummyPyparsingThingy())

def test_Matcher_match_doesnt_touch_results_on_failure():
    class DummyPyparsingThingy:
        def parseString(self, obj):
            raise ParseException(None, None, None)
    sentinel = object()
    m = Matcher("foo")
    m.results = sentinel
    m.match(DummyPyparsingThingy())
    assert m.results is sentinel

from grailmud.utils import maybeinroom
from grailmud.actiondefs.core import object_pattern
from grailmud.rooms import AnonyRoom
from grailmud.objects import TargettableObject, MUDObject

class MockInfo:

    def __init__(self, instigator):
        self.instigator = instigator

class Test_maybeinroom(SetupHelper):

    def setUp(self):
        self.room = AnonyRoom()
        self.target = TargettableObject('a killer rabbit', set(['killer',
                                                                'rabbit']),
                                        self.room)
        self.actor = MUDObject(self.room)
        self.setup_for_object(self.actor)
        self.setup_for_object(self.target)
        self.goodblob, = object_pattern.parseString('killer rabbit')
        self.badblob, = object_pattern.parseString("bogus bunny")
        self.info = MockInfo(self.actor)

    def test_calls_on_success(self):
        called = []
        def on_success(res):
            called.append(True)
        def on_failure():
            assert False
        maybeinroom(self.goodblob, [self.room], self.info, on_success, 
                    on_failure)
        assert len(called) == 1

    def test_passes_target_on_success(self):
        called = []
        def on_success(res):
            called.append(res)
        def on_failure():
            assert False
        maybeinroom(self.goodblob, [self.room], self.info, on_success,
                    on_failure)
        assert called == [self.target]

    def test_calls_on_failure(self):
        called = []
        def on_failure():
            called.append(True)
        def on_success(res):
            print res
            assert False
        maybeinroom(self.badblob, [self.room], self.info, on_success,
                    on_failure)
        assert len(called) == 1

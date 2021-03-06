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

from grailmud.actiondefs.deaf import DeafnessOnEvent, DeafnessOnAlreadyEvent, \
                                   DeafnessOffEvent, DeafnessOffAlreadyEvent, \
                                   deafDistributor, deafOn, deafOff, register, \
                                   syntaxmessage
from grailmud.actiondefs.system import BadSyntaxEvent
from grailmud.objects import MUDObject
from grailmud.events import AudibleEvent
from grailmud.utils_for_testing import SetupHelper

def test_registration():
    d = {}
    register(d)
    assert d['deaf'] is deafDistributor

def test_deafness_turning_on():
    obj = MUDObject(None)
    deafOn(obj)
    assert obj.deaf

def test_deafness_turning_off():
    obj = MUDObject(None)
    obj.deaf = True
    deafOff(obj)
    assert not obj.deaf

def test_default_deafness():
    assert not MUDObject(None).deaf

class TestActionsAndEvents(SetupHelper):

    def setUp(self):
        self.obj = MUDObject(None)
        self.setup_for_object(self.obj)
        
    def test_deaf_on_success(self):
        deafOn(self.obj)

        assert self.obj.delegate.received == [DeafnessOnEvent()], \
               "self.delegate.received is %r" % self.delegate.received

    def test_deaf_on_failure(self):
        self.obj.deaf = True
        deafOn(self.obj)

        assert self.obj.delegate.received == [DeafnessOnAlreadyEvent()], \
               "self.delegate.received is %r" % self.delegate.received

    def test_deaf_off_failure(self):
        deafOff(self.obj)

        assert self.obj.delegate.received == [DeafnessOffAlreadyEvent()], \
               "self.delegate.received is %r" % self.delegate.received

    def test_deaf_off_success(self):
        self.obj.deaf = True
        deafOff(self.obj)

        assert self.obj.delegate.received == [DeafnessOffEvent()], \
               "self.delegate.received is %r" % self.delegate.received

    def test_deaf_on_success_with_parsing(self):
        deafDistributor(self.obj, 'on', None)

        assert self.obj.delegate.received == [DeafnessOnEvent()], \
               "self.delegate.received is %r" % self.delegate.received

    def test_deaf_on_failure_with_parsing(self):
        self.obj.deaf = True
        deafDistributor(self.obj, 'on', None)

        assert self.obj.delegate.received == [DeafnessOnAlreadyEvent()], \
               "self.delegate.received is %r" % self.delegate.received

    def test_deaf_off_failure_with_parsing(self):
        deafDistributor(self.obj, 'off', None)

        assert self.obj.delegate.received == [DeafnessOffAlreadyEvent()], \
               "self.delegate.received is %r" % self.delegate.received

    def test_deaf_off_success_with_parsing(self):
        self.obj.deaf = True
        deafDistributor(self.obj, 'off', None)

        assert self.obj.delegate.received == [DeafnessOffEvent()], \
               "self.delegate.received is %r" % self.delegate.received

    def test_interesting_but_correct_syntaxes(self):
        for cmd in ["  %s", "%s ", "\t%s  ", "%s\t", "\t %s", "\r\t%s",
                    "%s\r ", "%s \r   ", "%s", "%s \t", "%s foo",
                    "%sbar"]:
            
            deafDistributor(self.obj, cmd % 'on', None)
            deafDistributor(self.obj, cmd % 'off', None)
            assert self.obj.delegate.received == [DeafnessOnEvent(),
                                                  DeafnessOffEvent()], \
                   "Failed on %r, self.delegate.received is %r" % \
                   (cmd, self.delegate.received)
            self.obj.delegate.received = []
            
            deafDistributor(self.obj, cmd % 'ON', None)
            deafDistributor(self.obj, cmd % 'OFF', None)
            assert self.obj.delegate.received == [DeafnessOnEvent(),
                                                  DeafnessOffEvent()], \
                   "Failed on %r, self.delegate.received is %r" % \
                   (cmd, self.delegate.received)
            self.obj.delegate.received = []

    def test_wrong_syntax(self):
        for cmd in ['this', 'is', 'all wrong', 'and', 'should', 'not', 'turn',
                    'it on', 'or off']:
            deafDistributor(self.obj, cmd, None)
            assert self.obj.delegate.received == \
                                              [BadSyntaxEvent(syntaxmessage)],\
                   "Failed on %r, self.delegate.received is %r" % \
                   (cmd, self.delegate.received)
            self.obj.delegate.received = []

    def test_AudibleEvent_filtering(self):
        self.obj.deaf = True
        self.obj.receiveEvent(AudibleEvent())
        print self.obj.delegate.received
        assert self.obj.delegate.received == []

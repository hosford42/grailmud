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

from grailmud.telnet import LoggerIn, ConnectionHandler
import grailmud
from grailmud.rooms import AnonyRoom

class MockTicker:

    def add_command(self, func):
        func()

grailmud.instance.ticker = MockTicker()
grailmud.instance.startroom = AnonyRoom()

def test_callback_calling():
    l = LoggerIn()
    called = []
    l.callback = lambda line: called.append(line)
    line = "foobarbaz"
    l.lineReceived(line)
    assert called == [line]

def test_lost_connection_callback_calling():
    l = LoggerIn()
    called = []
    l.connection_lost_callback = lambda: called.append(None)
    l.connectionLost(None)
    assert called

def test_ConnectionHandler_initialisation():
    sentinel = object()
    ch = ConnectionHandler(sentinel)
    assert ch.telnet is sentinel

class MockTelnet:

    def __init__(self):
        self.written = ''

    def write(self, data):
        self.written += data

    def close(self):
        pass

def test_ConnectionHandler_write():
    telnet = MockTelnet()
    ch = ConnectionHandler(telnet)
    ch.write("foo")
    assert telnet.written == "foo"

def test_ConnectionHandler_setcallback():
    telnet = MockTelnet()
    sentinel = object()
    ch = ConnectionHandler(telnet)
    ch.setcallback(sentinel)
    assert telnet.callback is sentinel

#XXX: tests for strconstrained

from grailmud.telnet import ChoiceHandler, LoginHandler

def test_ChoiceHandler_initial():
    telnet = MockTelnet()
    ch = ChoiceHandler(telnet)
    ch.initial()
    assert telnet.callback == ch.choice_made

def test_ChoiceHandler_choice_made_new_character():
    telnet = MockTelnet()
    ch = ChoiceHandler(telnet)
    ch.choice_made("1")
    assert isinstance(ch.successor, CreationHandler)
    assert telnet.callback == ch.successor.get_name

def test_ChoiceHandler_choice_made_login():
    telnet = MockTelnet()
    ch = ChoiceHandler(telnet)
    ch.choice_made("2")
    assert isinstance(ch.successor, LoginHandler)
    assert telnet.callback == ch.successor.get_name

def test_ChoiceHandler_choice_made_bad_input():
    telnet = MockTelnet()
    ch = ChoiceHandler(telnet)
    ch.choice_made("bogus")
    #since it doesn't set it, we have to test for setting
    assert not hasattr(telnet, "callback")

from grailmud.telnet import CreationHandler

class TestCreationhandler:
    def setUp(self):
        self.telnet = MockTelnet()
        self.ch = CreationHandler(self.telnet)

    def test_CreationHandler_initialisation(self):
        assert self.telnet.callback == self.ch.get_name

    def test_CreationHandler_get_name_setting(self):
        self.ch.get_name("foo")
        assert self.ch.name == "foo"

    def test_CreationHandler_name_with_numbers_failure(self):
        self.ch.get_name("foo3290")
        assert self.telnet.callback == self.ch.get_name

    def test_CreationHandler_get_name_success(self):
        self.ch.get_name("foobarbaz")
        print self.telnet.callback
        assert self.telnet.callback == self.ch.get_password

from grailmud.telnet import AvatarHandler
from grailmud.objects import Player, NamedObject
from grailmud.events import BaseEvent

class MockEvent(BaseEvent):

    def collapseToText(self, state, obj):
        state.sendEventLine("FOOBAR")

def test_AvatarHandler_initialisation_calls_login():
    def fake_login(actor):
        actor.login_called = True
        login(actor)

    from grailmud.actiondefs.login import login
    from grailmud import telnet
    telnet.login = fake_login

    mocktelnet = MockTelnet()
    avatar = mocktelnet.avatar = Player("michael", "", set(), {}, 
                                        grailmud.instance.startroom, '')
    ah = AvatarHandler(mocktelnet, avatar)

    assert avatar.login_called

class TestAvatarHandler:

    def setUp(self):
        if 'bob' in NamedObject._name_registry:
            del NamedObject._name_registry['bob']
        self.telnet = MockTelnet()
        self.avatar = self.telnet.avatar = \
                      Player("bob", "", set(), {}, 
                             grailmud.instance.startroom, '')
        self.ah = AvatarHandler(self.telnet, self.avatar)

    def test_initialisation_listener_adding(self):
        assert self.ah.connection_state in self.avatar.listeners

    def test_initialisation_room_adding(self):
        assert self.avatar in grailmud.instance.startroom

    def test_initialisation_callback_setting(self):
        assert self.telnet.callback == self.ah.handle_line

    def test_handle_line_correct(self):
        called = []
        self.avatar.receivedLine = (lambda line, info: 
                                            called.append(('rl', line, info)))
        self.avatar.eventFlush = lambda: called.append(('ef',))
        self.ah.handle_line('foo')
        assert called == [('rl', 'foo', LineInfo(instigator = self.avatar)),
                          ('ef',)]

    def test_handle_line_removing_bad_characters(self):
        lines = []
        self.avatar.receivedLine = lambda *a: lines.append(a)
        self.ah.handle_line("foo\xff")
        assert lines == [('foo', LineInfo(instigator = self.avatar))]

    #XXX: not tested: receivedLine/eventFlush raising an error.
    #XXX: nor is a player popping up outside the startroom

from grailmud.telnet import LineInfo

def test_LineInfo_equality():
    obj = object()
    assert LineInfo(instigator = obj) == LineInfo(instigator = obj)

#XXX: more tests

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

class MockTicker:

    def add_command(self, func):
        func()

grailmud.instance.ticker = MockTicker()

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

from grailmud.telnet import ChoiceHandler

def test_ChoiceHandler_initial():
    telnet = MockTelnet()
    ch = ChoiceHandler(telnet)
    ch.initial()
    assert telnet.callback == ch.choice_made

def test_ChoiceHandler_choice_made_new_character():
    telnet = MockTelnet()
    ch = ChoiceHandler(telnet)
    ch.choice_made("1")
    assert telnet.callback == ch.successor.get_name

def test_ChoiceHandler_choice_made_login():
    telnet = MockTelnet()
    ch = ChoiceHandler(telnet)
    ch.choice_made("2")
    assert telnet.callback == ch.successor.get_name

def test_ChoiceHandler_choice_made_bad_input():
    telnet = MockTelnet()
    ch = ChoiceHandler(telnet)
    ch.choice_made("bogus")
    #since it doesn't set it, we have to test for setting
    assert not hasattr(telnet, "callback")

from grailmud.telnet import CreationHandler

def test_CreationHandler_initialisation():
    telnet = MockTelnet()
    ch = CreationHandler(telnet)
    assert telnet.callback == ch.get_name

#XXX: more tests

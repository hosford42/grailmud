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

from grailmud.telnet import LoggerIn
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

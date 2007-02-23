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

from grailmud.objects import MUDObject
from grailmud.utils_for_testing import SetupHelper
from grailmud.actiondefs.more import displayMore, MoreEvent, NoMoreEvent, register
from grailmud.morelimiter import MoreLimiter
from grailmud.events import BaseEvent

def test_registration():
    d = {}
    register(d)
    assert d['more']

class TestMore(SetupHelper):

    def setUp(self):
        self.obj = MUDObject(None)
        self.obj.more_limiter = MoreLimiter(10)
        self.setup_for_object(self.obj)

    def test_more_event(self):
        data = "foo\n" * 29
        self.obj.chunks = self.obj.more_limiter.chunk(data)
        
        displayMore(self.obj)
        assert self.obj.listener.received == [MoreEvent('foo\n' * 10,
                                                        30, 20)]
        self.obj.listener.received = []
        displayMore(self.obj)
        assert self.obj.listener.received == [MoreEvent('foo\n' * 10,
                                                        30, 10)]
        self.obj.listener.received = []
        displayMore(self.obj)
        assert self.obj.listener.received == [MoreEvent('foo\n' * 9,
                                                        30, 0)]
        self.obj.listener.received = []

    def test_no_more_event(self):
        self.obj.chunks = self.obj.more_limiter.chunk('')

        displayMore(self.obj)
        self.obj.listener.received = []
        
        displayMore(self.obj)
        assert self.obj.listener.received == [NoMoreEvent()]

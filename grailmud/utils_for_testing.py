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

class MockListener(object):

    def __init__(self, obj = None):
        self.received = []
        self.flushed = False
        if obj is not None:
            self.obj = obj
            self.obj.listener = self

    def register(self, obj):
        if hasattr(self, 'obj'):
            assert obj is self.obj
            assert self in obj.listeners
        else:
            self.obj = obj
            obj.listener = self

    def unregister(self, obj):
        assert obj is self.obj
        assert self not in obj.listeners

    def listenToEvent(self, obj, event):
        assert obj is self.obj
        self.received.append(event)

    def eventListenFlush(self, obj):
        assert obj is self.obj
        self.flushed = True

class SetupHelper(object):

    def setup_for_object(self, obj):
        if hasattr(self, 'room'):
            self.room.add(obj)
        obj.listener = MockListener()
        obj.addListener(obj.listener)

    def setUp(self):
        self.obj = MUDObject(None)
        self.setup_for_object(self.obj)

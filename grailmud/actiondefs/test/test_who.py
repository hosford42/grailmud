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

from grailmud.actiondefs.who import WhoHereEvent, WhoEvent, whoHere, \
                                    whoDistributor, who, register
from grailmud.utils_for_testing import SetupHelper
from grailmud.objects import MUDObject
from grailmud.rooms import AnonyRoom

def test_registration():
    d = {}
    register(d)
    assert d['who'] is whoDistributor

class TestEventSending(SetupHelper):

    def setUp(self):
        self.room = AnonyRoom()
        self.actor = MUDObject(self.room)
        self.setup_for_object(self.actor)

    def test_whoHere_event_sending(self):
        whoHere(self.actor)
        assert self.actor.listener.received == \
                                           [WhoHereEvent(self.room.contents)]

    def test_who_event_sending(self):
        who(self.actor)
        assert self.actor.listener.received == [WhoEvent(self.actor)]

    def test_who_here_parsing(self):
        whoDistributor(self.actor, "here", None)
        assert self.actor.listener.received == \
                                           [WhoHereEvent(self.room.contents)]

    def test_who_parsing_default(self):
        whoDistributor(self.actor, "bogus option", None)
        assert self.actor.listener.received == [WhoEvent(self.actor)]

    def test_who_parsing_blank(self):
        whoDistributor(self.actor, "", None)
        assert self.actor.listener.received == [WhoEvent(self.actor)]



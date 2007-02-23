from __future__ import absolute_import

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

import logging
from grailmud.strutils import capitalise
from grailmud.events import SystemEvent
from grailmud.utils import promptcolour, distributeEvent

class LoginThirdEvent(SystemEvent):

    def __init__(self, actor):
        self.actor = actor

    @promptcolour()
    def collapseToText(self, state, obj):
        state.sendEventLine("%s's form appears, and they crackle into life." %
                            capitalise(self.actor.dsesc))

class LoginFirstEvent(SystemEvent):

    def collapseToText(self, state, obj):
        state.setColourName('normal')
        state.sendEventLine("Welcome to the game.")

def login(actor):
    '''Perform some initialisation for the Player being logged in.'''
    actor.connstate = 'online'
    actor.chunked_event = None
    actor.chunks = iter([])
    actor.receiveEvent(LoginFirstEvent())
    distributeEvent(actor.room, [actor], LoginThirdEvent(actor))

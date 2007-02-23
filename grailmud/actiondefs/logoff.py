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
from grailmud.events import SystemEvent
from grailmud.utils import promptcolour, distributeEvent
from grailmud.strutils import capitalise

class LogoffFirstEvent(SystemEvent):

    @promptcolour()
    def collapseToText(self, state, obj):
        state.sendEventLine("Goodbye!")
        state.dontWantPrompt()

class LogoffThirdEvent(SystemEvent):

    def __init__(self, actor):
        self.actor = actor

    @promptcolour()
    def collapseToText(self, state, obj):
        state.sendEventLine("%s has left the game." %
                            capitalise(self.actor.sdesc))


def quitGame(actor, text, info):
    if info.instigator is not actor:
        info.instigator.receiveEvent(PermissionDeniedEvent())
    else:
        logoffFinal(actor)

def logoffFinal(actor):
    #XXX: is this doing stuff in the correct order?
    if actor.connstate != 'online':
        logging.info("Foiled a double logoff attempt with %r." % actor)
        return
    actor.connstate = 'offline'
    actor.receiveEvent(LogoffFirstEvent())
    distributeEvent(actor.room, [actor], LogoffThirdEvent(actor))
    actor.disconnect()
    actor.room.remove(actor)

def register(cdict):
    cdict['qq'] = quitGame
    cdict['quit'] = quitGame

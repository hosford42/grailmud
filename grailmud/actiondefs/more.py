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

from grailmud.events import SystemEvent
from grailmud.utils import promptcolour

class MoreEvent(SystemEvent):

    def __init__(self, text, initial, current):
        self.text = text
        self.initial = initial
        self.current = current

    @promptcolour()
    def collapseToText(self, state, obj):
        state.sendEventLine(self.text)
        state.sendEventLine("Type MORE to continue reading -- %d lines left "
                            "to show, out of %d." %
                            (self.current, self.initial))

class NoMoreEvent(SystemEvent):

    @promptcolour()
    def collapseToText(self, state, obj):
        state.sendEventLine("There is no more. Don't both asking for any.")

def displayMore(actor):
    try:
        data = actor.chunks.next()
    except StopIteration:
        actor.receiveEvent(NoMoreEvent())
    else:
        actor.receiveEvent(MoreEvent(data, actor.chunks.initial_lines,
                                     actor.chunks.lines_left))

def register(cdict):
    cdict['more'] = lambda actor, text, info: displayMore(actor)

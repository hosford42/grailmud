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

from pyparsing import ParseException, Literal
from grailmud.strutils import printable
from grailmud.events import AudibleEvent, GameEvent
from grailmud.cleanimporter import CleanImporter
from grailmud.objects import MUDObject
from grailmud.utils import defaultinstancevariable
from .system import badSyntax
from grailmud.utils import promptcolour

class DeafnessOnEvent(GameEvent):

    @promptcolour()
    def collapseToText(self, state, obj):
        state.sendEventLine("You forcibly shut out all sound, making the world"
                            "silent. Aah. Silence is golden.")

class DeafnessOnAlreadyEvent(GameEvent):

    @promptcolour()
    def collapseToText(self, state, obj):
        state.sendEventLine("You're already deaf, silly!")

class DeafnessOffEvent(GameEvent):

    @promptcolour()
    def collapseToText(self, state, obj):
        state.sendEventLine("You once again begin to hear sounds from the "
                            "world around you.")
            

class DeafnessOffAlreadyEvent(GameEvent):

    @promptcolour()
    def collapseToText(self, state, obj):
        state.sendEventLine("You're not deaf, silly!")

on_pattern = Literal('on')
off_pattern = Literal('off')

syntaxmessage = "Use 'deaf on' to turn deafness on, or 'deaf off' to turn "\
                "deafness off."

def deafDistributor(actor, rest, lineinfo):
    rest = rest.lower()
    try:
        on_pattern.parseString(rest)
    except ParseException:
        pass
    else:
        deafOn(actor)
        return
    try:
        off_pattern.parseString(rest)
    except ParseException:
        pass
    else:
        deafOff(actor)
        return
    badSyntax(actor, syntaxmessage)

def deafOn(actor):
    if not actor.deaf:
        actor.deaf = True
        actor.receiveEvent(DeafnessOnEvent())
    else:
        actor.receiveEvent(DeafnessOnAlreadyEvent())

def deafOff(actor):
    if not actor.deaf:
        actor.receiveEvent(DeafnessOffAlreadyEvent())
    else:
        actor.deaf = False
        actor.receiveEvent(DeafnessOffEvent())

@defaultinstancevariable(MUDObject, "deaf")
def deaf_default(self):
    return False

@MUDObject.receiveEvent.register(MUDObject, AudibleEvent)
def receiveEvent(self, event):
    """Ignore sound events for deaf things."""
    if not self.deaf:
        MUDObject.receiveEvent.call_next_method(self, event)

def register(cdict):
    cdict['deaf'] = deafDistributor

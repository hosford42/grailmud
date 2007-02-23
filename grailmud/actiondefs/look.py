from __future__ import with_statement
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

from grailmud.cleanimporter import CleanImporter
from .core import object_pattern
from grailmud.events import VisibleEvent
from grailmud.rooms import UnfoundError
from .system import unfoundObject
from grailmud.objects import Player, TargettableObject, ExitObject, MUDObject
from grailmud.strutils import capitalise
from grailmud.utils import promptcolour, get_from_rooms, distributeEvent
from grailmud.multimethod import Multimethod
from pyparsing import ParseException

class LookAtEvent(VisibleEvent):

    def __init__(self, target):
        self.target = target

    @promptcolour()
    def collapseToText(self, state, obj):
        state.sendEventLine(capitalise(self.target.ldesc))

class LookRoomEvent(VisibleEvent):

    def __init__(self, room):
        self.room = room

    @promptcolour("room title")
    def collapseToText(self, state, obj):
        state.sendEventLine(self.room.title)
        state.setColourName("room desc")
        state.sendEventLine(self.room.desc)
        state.setColourName("people list")
        peopleList = ["%s is here." % capitalise(obj.sdesc)
                      for obj in self.room.contents]
        state.sendEventLine(" ".join(peopleList))

with CleanImporter('pyparsing'):
    lookAtPattern = Suppress(Optional(Keyword("at"))) + \
                    object_pattern

def lookDistributor(actor, text, info):
    try:
        blob, = lookAtPattern.parseString(text)
    except ParseException:
        lookRoom(actor)
        return
    try:
        target = get_from_rooms(blob, [actor.inventory, actor.room], info)
    except UnfoundError:
        unfoundObject(actor)
    else:
        lookAt(actor, target)

lookAt = Multimethod()

@lookAt.register(MUDObject, MUDObject)
def lookAt(actor, target):
    unfoundObject(actor)

@lookAt.register(MUDObject, TargettableObject)
def lookAt(actor, target):
    if target.room not in [actor.inventory, actor.room]:
        unfoundObject(actor)
    else:
        actor.receiveEvent(LookAtEvent(target))

@lookAt.register(MUDObject, ExitObject)
def lookAt(actor, target):
    if target.room is not actor.room: #stricter deliberately.
        unfoundObject(actor)
    else:
        actor.receiveEvent(LookRoomEvent(target.target_room))

def lookRoom(actor):
    actor.receiveEvent(LookRoomEvent(actor.room))

def register(cdict):
    cdict['l'] = lookDistributor
    cdict['look'] = lookDistributor

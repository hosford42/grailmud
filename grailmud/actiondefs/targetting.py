from __future__ import absolute_import
from __future__ import with_statement

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
from grailmud.events import BaseEvent
from grailmud.objects import MUDObject
from grailmud.utils import promptcolour, get_from_rooms, \
        defaultinstancevariable
from grailmud.rooms import UnfoundError
from .core import object_pattern, shorttarget_pattern
from .system import permissionDenied, badSyntax, unfoundObject
from pyparsing import ParseException

@defaultinstancevariable(MUDObject, "targetting_shorts")
def targetting_shorts_default(self):
    return {}

class TargetSetEvent(BaseEvent):
    '''A target's been set to a value.'''
    def __init__(self, name, target):
        self.name = name
        self.target = target

    @promptcolour()
    def collapseToText(self, state, obj):
        state.sendEventLine('You may now refer to %s as $%s.'
                            % (self.target.sdesc, self.name))

class TargetClearedEvent(BaseEvent):
    '''An existing target has been cleared.'''
    def __init__(self, name):
        self.name = name

    @promptcolour()
    def collapseToText(self, state, obj):
        state.sendEventLine("Target $%s cleared." % self.name)

class TargetAlreadyClearedEvent(BaseEvent):
    '''A nonexistant target was cleared.'''
    def __init__(self, name):
        self.name = name

    @promptcolour()
    def collapseToText(self, state, obj):
        state.sendEventLine("You have no target $%s." % self.name)

class TargetListEvent(BaseEvent):
    '''The user asked for a list of targets.'''
    def __init__(self, actor):
        self.actor = actor

    @promptcolour()
    def collapseToText(self, state, obj):
        state.sendEventLine("You have set these targets:")
        for name, obj in self.actor.targetting_shorts.itervalues():
            state.sendEventLine("%s: %s" % (name, obj.sdesc))

with CleanImporter('pyparsing'):
    # pylint: disable-msg= E0602
    target_set_pattern = Suppress('set') + shorttarget_pattern + \
                         Suppress('to') + object_pattern

    target_clear_pattern = Suppress('clear') + shorttarget_pattern

    target_list_pattern = Suppress('list')

def targetDistributor(actor, text, info):
    if info.instigator is not actor:
        permissionDenied(info.instigator)
        return
    try:
        (name,), blob = target_set_pattern.parseString(text)
    except ParseException:
        pass
    else:
        try:
            target = get_from_rooms(blob, [actor.inventory, actor.room], info)
        except UnfoundError:
            unfoundObject(actor)
        else:
            targetSet(actor, name.lower(), target)
        return
    try:
        (name,), = target_clear_pattern.parseString(text)
    except ParseException:
        pass
    else:
        targetClear(actor, name.lower())
        return
    try:
        target_list_pattern.parseString(text)
    except ParseException:
        pass
    else:
        targetList(actor)
        return
    badSyntax(actor)

def targetSet(actor, name, target):
    actor.targetting_shorts[name] = target
    actor.receiveEvent(TargetSetEvent(name, target))

def targetClear(actor, name):
    if name in actor.targetting_shorts:
        del actor.targetting_shorts[name]
        actor.receiveEvent(TargetClearedEvent(name))
    else:
        actor.receiveEvent(TargetAlreadyClearedEvent(name))

def targetList(actor):
    actor.receiveEvent(TargetListEvent(actor))

def register(cdict):
    cdict['target'] = targetDistributor

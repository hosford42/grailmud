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

class CommandListEvent(SystemEvent):
    
    def __init__(self, command_list):
        self.command_list = command_list

    @promptcolour()
    def collapseToText(self, state, obj):
        state.sendEventLine("The commands visible to you are:")
        for synonyms in self.command_list:
            state.sendEventLine(', '.join(synonyms))

class NoCommandListEvent(SystemEvent):

    def collapseToText(self, state, obj):
        state.sendEventLine("I don't know how you've managed this, but you "
                            "have no commands to list.")

def invert_dict(dictionary):
    res = {}
    for key, value in dictionary.iteritems():
        if value not in res:
            res[value] = set()
        res[value].add(key)
    return res

def list_commands(actor):
    if not hasattr(actor, 'cmdict'):
        actor.receiveEvent(NoCommandListEvent())
    else:
        inverted_command_dict = invert_dict(actor.cmdict)
        actor.receiveEvent(CommandListEvent(inverted_command_dict.values()))

def register(cdict):
    cdict['commands'] = lambda actor, rest, info: list_commands(actor)

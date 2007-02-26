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

from string import ascii_letters, digits
from grailmud.multimethod import Multimethod
from grailmud.rooms import UnfoundError
from grailmud.events import SystemEvent
import logging
from grailmud.cleanimporter import CleanImporter

#Some utilities.
with CleanImporter('pyparsing'):
    shorttarget_pattern = Group(Suppress('$') + Word(ascii_letters + digits))
    adjs_pattern = Group(Group(OneOrMore(Word(ascii_letters))) + 
                         Optional(Word(digits), "0"))

    object_pattern = Or(adjs_pattern, shorttarget_pattern)

class UnfoundActionEvent(SystemEvent):

    def collapseToText(self, state, obj):
        state.forcePrompt()
        state.setColourName('normal')
        state.sendEventLine("I don't understand. Syntax error?")

def unfoundAction(actor, text, info):
    actor.receiveEvent(UnfoundActionEvent())

def register(cdict):
    #wrapped in a lambda because default_factory calls it to produce the value
    cdict.default_factory = lambda: unfoundAction

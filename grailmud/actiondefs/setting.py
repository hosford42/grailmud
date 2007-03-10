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

from grailmud.events import BaseEvent
from grailmud.utils import promptcolour, defaultinstancevariable
from grailmud.objects import TargettableObject
from .system import badSyntax
from string import whitespace
from grailmud.strutils import wsnormalise, printable
from pyparsing import ParseException, Suppress, Word

class LDescSetEvent(BaseEvent):

    def __init__(self, desc):
        self.desc = desc

    @promptcolour("speech")
    def collapseToText(self, state, obj):
        state.sendEventLine("Your long descrption is now:")
        state.sendEventLine(self.desc)

    def __repr__(self):
        return "%s(%r)" % (type(self).__name__, self.desc)

#I don't know how or why this works, but it does.
ldesc_pattern = Suppress("ldesc") + Word(printable)

syntax_message = "'%r' is an unknown option for the 'set' action."

def setDistribute(actor, text, info):
    try:
        desc, = ldesc_pattern.parseString(text)
    except ParseException:
        badSyntax(actor, syntax_message % text)
    else:
        setLDesc(actor, desc)

def setLDesc(actor, desc):
    actor.ldesc = desc
    actor.receiveEvent(LDescSetEvent(desc))

class Dictator(object):

    def __init__(self, obj):
        self.obj = obj

    def __getitem__(self, name):
        if hasattr(self.obj, name):
            return getattr(self.obj, name)
        raise KeyError

class SmartDictWrapper(object):

    def __init__(self, d):
        self.d = d

    def __getitem__(self, name):
        #globanls can't be a dict, but locals can
        return eval(name, {}, self.d)

default_long_desc = "%(sdesc)s. Nothing more, nothing less."

@defaultinstancevariable(TargettableObject, "ldesc")
def construct_ldesc(self):
    return default_long_desc % SmartDictWrapper(Dictator(self))

def register(cdict):
    cdict['set'] = setDistribute

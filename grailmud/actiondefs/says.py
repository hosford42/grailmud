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

from .core import object_pattern
from grailmud.events import AudibleEvent
from .system import unfoundObject, badSyntax
from grailmud.rooms import UnfoundError
from grailmud.strutils import capitalise, printable
from grailmud.objects import MUDObject, TargettableObject
from grailmud.utils import promptcolour, distributeEvent, get_from_rooms
from grailmud.multimethod import Multimethod
from pyparsing import ParseException, Suppress, Word

class SpeakNormalFirstEvent(AudibleEvent):

    def __init__(self, text):
        self.text = text

    @promptcolour("speech")
    def collapseToText(self, state, obj):
        if not self.text:
            state.sendEventLine("You open your mouth, as if to say something, "
                                "and stay like that looking silly for a few "
                                "seconds before you finally realise you have "
                                "nothing to say.")
        else:
            state.sendEventLine('You say, "%s"' % self.text)

class SpeakNormalThirdEvent(AudibleEvent):

    def __init__(self, actor, text):
        self.actor = actor
        self.text = text

    @promptcolour("speech")
    def collapseToText(self, state, obj):
        d = capitalise(self.actor.sdesc)
        if not self.text:
            state.sendEventLine("%s opens their mouth, as if to say something,"
                                " but rescinds after a few seconds of silly "
                                "gaping." % d)
        else:
            state.sendEventLine('%s says, "%s"' % (d, self.text))

class SpeakToFirstEvent(AudibleEvent):

    def __init__(self, target, text):
        self.target = target
        self.text = text

    @promptcolour("speech")
    def collapseToText(self, state, obj):
        d = self.target.sdesc
        if not self.text:
            state.sendEventLine("You turn to %s and open your mouth, as if to "
                                "say something, but instead you gawp for a few"
                                " moments until you realise you have nothing "
                                "to say, and prompty close your mouth again."
                                % d)
        else:
            state.sendEventLine('You say to %s, "%s"' % (d, self.text))

class SpeakToSecondEvent(AudibleEvent):

    def __init__(self, actor, text):
        self.actor = actor
        self.text = text

    @promptcolour("speech")
    def collapseToText(self, state, obj):
        d = capitalise(self.actor.sdesc)
        if not self.text:
            state.sendEventLine("%s turns to you and opens their mouth, but "
                                "says nothing, as if to catch a fly. Realising"
                                " how silly they look, they promptly clamp "
                                "their jaw shut after a few seconds." % d)
        else:
            state.sendEventLine('%s says to you, "%s"' % (d, self.text))
                                
class SpeakToThirdEvent(AudibleEvent):

    def __init__(self, actor, target, text):
        self.actor = actor
        self.target = target
        self.text = text

    @promptcolour("speech")
    def collapseToText(self, state, obj):
        da = capitalise(self.actor.sdesc)
        dt = capitalise(self.actor.sdesc)
        if not self.text:
            state.sendEventLine("%s turns to %s and opens their mouth, but "
                                "says nothing, as if to catch a fly. Realising"
                                " how silly they look, they promptly clamp "
                                "their jaw shut after a few seconds."
                                % (da, dt))
        else:
            state.sendEventLine('%s says to %s, "%s"' % (da, dt, self.text))

speakToPattern = object_pattern + Suppress(',') + Word(printable)

def speakToWrapper(actor, text, info):
    try:
        res = speakToPattern.parseString(text)
        blob, saying = res
    except ParseException:
        badSyntax(actor, "Can't find the end of the target identifier. Use "
                         "',' at its end to specify it.")
        return
    try:
        target = get_from_rooms(blob, [actor.inventory, actor.room], info)
    except UnfoundError:
        unfoundObject(actor)
    else:
        speakTo(actor, target, saying)

def speak(actor, text):
    actor.receiveEvent(SpeakNormalFirstEvent(text))
    distributeEvent(actor.room, [actor], SpeakNormalThirdEvent(actor, text))

speakTo = Multimethod()

@speakTo.register(MUDObject, MUDObject, basestring)
def speakTo(actor, _, text):
    unfoundObject(actor)

@speakTo.register(MUDObject, TargettableObject, basestring)
def speakTo(actor, target, text):
    if target not in actor.room and target not in actor.inventory:
        unfoundObject(actor)
    else:
        actor.receiveEvent(SpeakToFirstEvent(target, text))
        target.receiveEvent(SpeakToSecondEvent(actor, text))
        distributeEvent(actor.room, [actor, target],
                        SpeakToThirdEvent(actor, target, text))

def register(cdict):
    cdict['say'] = cdict['"'] = cdict["'"] = \
                   lambda actor, text, info: speak(actor, text)
    cdict['say,'] = cdict["',"] = cdict['",'] = cdict['sayto'] \
                  = speakToWrapper

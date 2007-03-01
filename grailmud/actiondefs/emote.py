from __future__ import absolute_import
from __future__ import with_statement

"""Emotes/ At present, only user-customised, but eventually I'll get round to
writing some prefab ones.
"""

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
from string import printable
from grailmud.events import GameEvent
from grailmud.rooms import UnfoundError
from grailmud.utils import promptcolour, smartdict, get_from_rooms, \
                           distributeEvent
from grailmud.strutils import wsnormalise
from .core import object_pattern
from grailmud.actiondefs.system import badSyntax, unfoundObject
import pkg_resources

class EmoteUntargettedFirst(GameEvent):

    def __init__(self, actor, message):
        self.actor = actor
        self.message = message

    @promptcolour('emote')
    def collapseToText(self, state, obj):
        state.sendEventLine(self.message
                            % smartdict({'actor': self.actor}))

class EmoteUntargettedThird(GameEvent):

    def __init__(self, actor, message):
        self.actor = actor
        self.message = message

    @promptcolour('emote')
    def collapseToText(self, state, obj):
        state.sendEventLine(self.message % smartdict({'actor': self.actor}))

class EmoteTargettedFirst(GameEvent):

    def __init__(self, actor, target, message):
        self.actor = actor
        self.target = target
        self.message = message

    @promptcolour('emote')
    def collapseToText(self, state, obj):
        state.sendEventLine(self.message %
                            smartdict({'target': self.target,
                                       'actor': self.actor}))

class EmoteTargettedSecond(GameEvent):

    def __init__(self, actor, message):
        self.actor = actor
        self.message = message

    @promptcolour('emote')
    def collapseToText(self, state, obj):
        state.sendEventLine(self.message % smartdict({'actor': self.actor}))

class EmoteTargettedThird(GameEvent):

    def __init__(self, actor, target, message):
        self.actor = actor
        self.target = target
        self.message = message

    @promptcolour('emote')
    def collapseToText(self, state, obj):
        state.sendEventLine(self.message % smartdict({'actor': self.actor,
                                                      'target': self.target}))

def emoteWrapper(actor, text, info):
    text = text.replace('%', '%%')
    emote(actor, 'You have emoted: ' + text, text)

with CleanImporter('pyparsing'):
    emote_to_pattern = object_pattern + Suppress(',') + Word(printable)

def emoteToWrapper(actor, text, info):
    try:
        blob, text = emote_to_pattern.parseString(text)
    except ParseException:
        badSyntax()
        return
    try:
        target = get_from_rooms(blob, [actor.inventory, actor.room], info)
    except UnfoundError:
        unfoundObject()
        return
    text = text.replace('%', '%%')
    emoteTo(actor, target, 'You have emoted: ' + text, text, text)

def emote(actor, first, third):
    first = process(first)
    third = process(third)
    actor.receiveEvent(EmoteUntargettedFirst(actor, first))
    distributeEvent(actor.room, [actor],
                    EmoteUntargettedThird(actor, third))

def emoteTo(actor, target, first, second, third):
    if target.room not in [actor.room, actor.inventory]:
        unfoundObject()
        return
    first = process(first)
    second = process(second)
    third = process(third)
    actor.receiveEvent(EmoteTargettedFirst(target, first))
    target.receiveEvent(EmoteTargettedSecond(actor, second))
    distributeEvent(actor.room, [actor, target],
                    EmoteTargettedThird(actor, target, third))

class YankedUntargetted(object):

    def __init__(self, first, third = None):
        self.first = first
        self.third = third

    def __call__(self, actor, text, info):
        self.send_out_events(actor)

    def send_out_events(self, actor):
        if self.third is not None:
            emote(actor, self.first, self.third)
        else:
            #solipsism
            actor.receiveEvent(EmoteUntargettedFirst(actor, self.first))

class YankedTargetted(object):
    
    def __init__(self, first, second, third, fallback):
        self.first = first
        self.second = second
        self.third = third
        self.fallback = fallback

    def __call__(self, actor, text, info):
        try:
            blob, = object_pattern.parseString(text)
        except ParseException:
            pass
        else:
            try:
                target = get_from_rooms(blob, [actor.inventory, actor.room],
                                        info)
                self.send_out_events(actor, target)
            except UnfoundError:
                pass
            else:
                return
        self.fallback(actor)

    def send_out_events(self, actor, target):
        emoteTo(actor, target, self.first, self.second, self.third)

def yank_emotes(emotefile):
    emote_definitions = get_dict_definitions(emotefile)
    for definition in emote_definitions:
        if 'untargetted' in definition:
            function = untargetted = \
                                 YankedUntargetted(**definition['untargetted'])
        else:
            untargetted = unfoundObject
        if 'targetted' in definition:
            function = YankedTargetted(fallback = untargetted,
                                       **definition['targetted'])
        for name in definition['names']:
            yield name, function

def get_dict_definitions(emotefile):
    '''This transforms a list of emote definitions into a list of dictionaries.
    '''
    lines = iter(emotefile.split('\n'))
    curemote = {'untargetted': {}}
    for line in lines:
        if line.startswith('emotedef:'):
            curemote['names'] = line.partition(':')[2].replace(' ', '').\
                                                       split(',')
        if line == 'untargetted':
            line = lines.next()
            while line.startswith('first') or line.startswith('third'):
                part, _, emote = line.partition(':')
                line = lines.next()
                curemote['untargetted'][part] = emote.strip()
        if line == 'targetted':
            curemote['targetted'] = {}
            line = lines.next()
            while line.startswith('first') or line.startswith("second") or \
                  line.startswith("third"):
                part, _, emote = line.partition(':')
                curemote['targetted'][part] = emote.strip()
                line = lines.next()
        if not line or line.isspace():
            if curemote != {'untargetted': {}}:
                yield curemote
                curemote = {'untargetted': {}}
    if curemote != {'untargetted': {}}:
        yield curemote

def register(cdict):
    cdict['emote'] = emoteWrapper
    cdict['emoteto'] = emoteToWrapper
    cdict['emote,'] = emoteToWrapper

    #XXX: make working. Commented out because it refuses to work.
#    emotefile = pkg_resources.resource_string(__name__, "emotefile.txt")
#    for name, yanked_emote in yank_emotes(emotefile):
#        cdict[name] = yanked_emote
#        yanked_emotes[name] = yanked_emote.send_out_events
    
def process(text):
    text = wsnormalise(text)
    text = text.replace(' ~', ' %(actor.sdesc)s')
    text = text.replace(' @', ' %(target.sdesc)s')
    return text

yanked_emotes = {}

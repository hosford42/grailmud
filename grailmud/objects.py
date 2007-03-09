"""This file contains an implementation of objects in the MUD and a simple
interface for hooking them up with listeners and events.
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

import logging
from grailmud.strutils import head_word_split
from grailmud.rooms import Room
from grailmud.multimethod import Multimethod
from grailmud.events import BaseEvent
from grailmud.utils import BothAtOnce

#TODO: some sort of way to tell the classes not to pickle certain attributes.
#XXX: need some sort of implementation for stateless, groupable objects.
#XXX: the metaclass/class hierarchy is a bit fragile.

class MUDObject(BothAtOnce):
    """An object in the MUD."""
    
    def __init__(self, room):
        self.room = room
        self.listeners = set()
        self.inventory = Room("A dummy inventory.", "This is a dummy "
                              "inventory, to make the checking code a little "
                              "bit simpler.")
    
    def eventFlush(self):
        """Tell the listeners that the current lot of events are done."""
        for listener in self.listeners:
            listener.eventListenFlush(self)

    def addListener(self, listener):
        """Register a new listener.

        Throws a ValueError if it's already listening."""
        if listener in self.listeners:
            raise ValueError("Listener is already listening.")
        self.listeners.add(listener)
        listener.register(self)

    def removeListener(self, listener):
        """Remove a listener. Throws errors if it's not currently listening.
        """
        if listener not in self.listeners:
            raise ValueError("Listener is not listening.")
        self.listeners.remove(listener)
        listener.unregister(self)

    #XXX: these two methods should be reimplemented as events.
    def transferControl(self, obj):
        """Utility method to shift all the listeners to another object."""
        for listener in self.listeners:
            listener.transferControl(self, obj)

    def disconnect(self):
        '''Notify the listeners that this object is being disconnected.

        Note that this only makes sense for Players, but it needs to be on
        here else AttributeErrors will start flying around. I think. So we
        just ignore it.
        '''
        pass

    def __getstate__(self):
        listeners = set(listener for listener in self.listeners
                        if listener._pickleme)
        state = BothAtOnce.__getstate__(self)
        state['listeners'] = listeners
        return state

    receiveEvent = Multimethod()

@MUDObject.receiveEvent.register(MUDObject, BaseEvent)
def receiveEvent(self, event):
    """Receive an event in the MUD.

    This is the very basic handler for objects that can be listened to.
    """
    for listener in self.listeners:
        listener.listenToEvent(self, event)

class TargettableObject(MUDObject):
    """A tangible object, that can be generically targetted."""
    
    def __init__(self, sdesc, adjs, room):
        self.sdesc = sdesc
        self.adjs = adjs
        super(TargettableObject, self).__init__(room)
    
    def match(self, attrs):
        """Check to see if a set of attributes is applicable for this object.
        """
        return self.adjs.issuperset(attrs)

class NamealreadyUsedError(BaseException):
    pass

class NamedObject(TargettableObject):

    #XXX: make me a proper caseless dict?
    _name_registry = {}
    
    def __init__(self, sdesc, name, adjs, room):
        if NamedObject.exists(name):
            raise NamealreadyUsedError()
        super(NamedObject, self).__init__(sdesc, adjs, room)
        self.inventory = Room("%s's inventory" % name,
                              "You should not be here.")
        NamedObject._name_registry[name.lower()] = self
        self.name = name
        self.adjs = adjs | set([name.lower()])
    
    def match(self, attrs):
        """Check to see if a set of attributes is applicable for this object.
        """
        return attrs == set([self.name]) or \
               TargettableObject.match(self, attrs)

    @classmethod
    def exists(cls, name):
        '''Returns True if an object referred to by a given name exists.'''
        try:
            avatar = NamedObject._name_registry[name.lower()]
        except KeyError:
            return False
        else:
            return isinstance(avatar, cls)

    def __repr__(self):
        return "<%s named %s>" % (type(self).__name__, self.name)

class Player(NamedObject):
    """A player avatar."""

    def __init__(self, name, sdesc, adjs, room, passhash):
        self.connstate = 'online'
        self.passhash = passhash
        super(Player, self).__init__(sdesc, name, adjs, room)

    def receivedLine(self, line, info):
        """Receive a single line of input to process and act upon."""
        cmd, rest = head_word_split(line)
        logging.debug("cmd is %r." % cmd)
        func = self.cmdict[cmd.lower()]
        logging.debug("Command found in cmdict, function is %r" % func)
        func(self, rest, info)

    def disconnect(self):
        '''Notify the listeners that we are being disconnected.'''
        for listener in self.listeners.copy(): #copy because we mutate it
            listener.disconnecting(self)
            #no self.removeListener(listener) here because it's a little silly
            #to not have it implied.

    def __getstate__(self):
        #is using super correct here?
        state = NamedObject.__getstate__(self)
        state['connstate'] = 'offline'
        if 'cmdict' in state:
            del state['cmdict']
        if 'chunks' in state:
            del state['chunks']
        return state

    def __setstate__(self, state):
        NamedObject.__setstate__(self, state)

    @staticmethod
    def get(name, passhash):
        #XXX: refactor this to telnet.py?
        """Get the avatar referred to by name, but only if its passhash is
        equal.

        Throws KeyErrors if the name is garbage.
        """
        if not Player.exists(name):
            raise KeyError("name is not the name of a player")
        avatar = NamedObject._name_registry[name]
        if passhash != avatar.passhash:
            raise BadPassword()
        return avatar

class ExitObject(MUDObject):
    """An exit."""

    def __init__(self, room, target_room):
        self.target_room = target_room
        super(ExitObject, self).__init__(room)

class TargettableExitObject(ExitObject):

    def __init__(self, room, target_room, sdesc, adjs):
        self.sdesc = sdesc
        self.adjs = adjs
        super(TargettableExitObject, self).__init__(room, target_room)

    def match(self, adjs):
        return self.adjs.issuperset(adjs)

class BadPassword(Exception):
    pass


'''This class has some base classes for events.'''

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

class BaseEvent(object):
    '''The root of all events.'''

    def collapseToText(self, state, obj):
        """Transform the event into text via the state. The obj is the object
        that received the event in the first place.
        """
        raise NotImplementedError("Base class.")

    def __eq__(self, other):
        return type(self) == type(other) and self.__dict__ == other.__dict__

class SystemEvent(BaseEvent):
    '''An event which comes from the system (ie, the implementation).'''
    pass

class GameEvent(BaseEvent):
    '''An event which comes from the game (ie, the world).'''
    pass

class AudibleEvent(GameEvent):
    '''An event you can hear.'''
    pass

class VisibleEvent(GameEvent):
    '''An event you can see.'''
    pass

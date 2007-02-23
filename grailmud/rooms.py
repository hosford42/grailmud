"""Contains some classes for dealing with containers."""

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

from grailmud.orderedset import OrderedSet
from grailmud.utils import InstanceTracker

class UnfoundError(Exception):
    """The object wasn't found."""
    pass


class AnonyRoom(InstanceTracker):
    """A room without a title or description."""

    def __init__(self):
        self.contents = OrderedSet()
        InstanceTracker.__init__(self)

    def add(self, obj):
        """Add an object to the room. Does not modify the object to reflect
        this.
        """
        self.contents.add(obj)

    def remove(self, obj):
        """Remove an object from the room. Does not modify the object to reflect
        this.
        """
        self.contents.remove(obj)

    def matchContent(self, attrs, count, test = (lambda x: True)):
        """Looks for an object matching the given criteria in the room.

        attrs is a set of attributes the object must have. count is the number
        of the object in the room. test is an optional function to check the
        object up against.

        This function may or may not be deprecated.
        """
        for obj in self.matchContentAll(attrs):
            if test(obj):
                if count == 0:
                    return obj
                else:
                    count -= 1
        raise UnfoundError()

    def matchContentAll(self, attrs):
        """Return an iterator that yields all the objects that match a certain
        set of attributes.
        """
        for obj in self:
            if hasattr(obj, 'match') and obj.match(attrs):
                yield obj

    def __contains__(self, obj):
        return obj in self.contents

    def __iter__(self):
        return iter(self.contents)
        
class Room(AnonyRoom):
    """A single container or 'room'."""

    def __init__(self, title, desc):
        self.title = title
        self.desc = desc
        AnonyRoom.__init__(self)



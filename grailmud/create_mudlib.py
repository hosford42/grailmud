
"""Instantiate the MUDlib and write it to disk."""

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

import os
from durus.file_storage import FileStorage
from durus.connection import Connection
from grailmud.rooms import Room
from grailmud.objects import MUDObject, NamedObject
from grailmud.npcs.chatty import ChattyListener
from grailmud.ticks import Ticker

startroom = Room('An unremarkable moor.',
                 'This moor is extremely bare. Overly so, perhaps. There '
                 'is a definite air of blandness about its grey horizon '
                 'and overcast sky. The ground is anonymous and blank; '
                 'grey dust litters the floor, and that is about all which '
                 'can be said about it. Even the air seems to be steeped in'
                 ' mediocrity - a lukewarm temperature, with no discernable'
                 ' exciting scents.')

eliza = NamedObject('a bespectacled old lady', 'Eliza',
                    set(['old', 'lady', 'woman']), startroom)
eliza.addListener(ChattyListener(eliza))
startroom.add(eliza)

if os.access("mudlib.durus", os.F_OK):
    os.remove("mudlib.durus")

try:
    connection = Connection(FileStorage("mudlib.durus"))

    root = connection.get_root()

    # pylint: disable-msg= E1101,W0212
    #pylint doesn't know about our metaclass hackery, and complains about the
    #use of the leading underscore variables.
    root['startroom'] = startroom
    root['all_rooms'] = Room._instances
    root['all_objects'] = MUDObject._instances
    root['targettable_objects_by_name'] = NamedObject._name_registry
    root['ticker'] = Ticker(0.1)
    # pylint: enable-msg= E1101,W0212

    connection.commit()
except:
    connection.abort()
    #if os.access("mudlib.durus", os.F_OK):
    #    os.remove("mudlib.durus")
    raise

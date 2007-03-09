"""Handles server initialisation and pulls some Twisted ropes."""

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
import grailmud
from twisted.internet.protocol import Factory
from grailmud.telnet import LoggerIn
from grailmud.rooms import Room
from grailmud.objects import MUDObject, NamedObject, Player
from twisted.internet import reactor

class ConnectionFactory(Factory):
    """The actual server factory."""

    protocol = LoggerIn

    def __init__(self, objstorethunk):
        grailmud.instance._bind(self)
        self.objstore = objstorethunk()
        self.root = self.objstore.get_root()
        #these look like no-ops, but they're not. Accessing them ought to 
        #unpickle everything, and thus insert them into _instances and whatnot.
        self.root['all_rooms']
        self.root['all_objects']
        for playerobj in Player._instances:
            if playerobj in playerobj.room:
                playerobj.room.remove(playerobj)
        NamedObject._name_registry = \
                                      self.root['targettable_objects_by_name']
    
    @property
    def ticker(self):
        return self.root['ticker']

    @property
    def startroom(self):
        return self.root['startroom']

def commit_gameworld():
    #XXX: could be made more efficient by not re-committing everything, but
    #that would require making everything (and I mean -everything-) mutability
    #conscious.
    try:
        root = grailmud.instance.root
        root['all_rooms'] = Room._instances
        root['all_objects'] = MUDObject._instances
        root['targettable_objects_by_name'] = NamedObject._name_registry
        root['ticker'] = grailmud.instance.ticker
        grailmud.instance.objstore.commit()
        grailmud.instance.objstore.pack()
        grailmud.instance.ticker.add_command(commit_gameworld)
    except:
        logging.error("commit_gameworld experienced an error. Stopping the "
                      "reactor.")
        reactor.stop()
        raise

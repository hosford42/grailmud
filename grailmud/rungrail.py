# pylint: disable-msg=E1101
#twisted does some hackery with the reactor that pylint doesn't know about.
"""This module is intended to be the main entry point for the server, run from
the shell.
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

from durus.file_storage import FileStorage
from durus.connection import Connection
from grailmud.server import ConnectionFactory
from twisted.internet import reactor
import sys
import logging

logging.basicConfig(level = logging.DEBUG,
                    format = '%(asctime)s %(levelname)s %(message)s',
                    stream = file('log.txt', 'w'))

def construct_mud(objstorethunk):
    """Construct a MUD factory."""
    return ConnectionFactory(objstorethunk)

def run_mud(mud, port):
    """Run the MUD factory."""
    reactor.listenTCP(port, mud)
    mud.ticker.start()
    logging.info("OK, setup done, handing you over to the reactor's loop!")
    sys.stdout.write("Server is up and running.")
    reactor.run()

if __name__ == '__main__':
    #this needs to be wrapped in a lambda, because Durus is quite eager to load
    #stuff. If it wasn't so eager, the ConnectionFactory would just pull what
    #it needed when, rather than getting silly errors on the next line.
    connection = lambda: Connection(FileStorage("mudlib.durus"))
    run_mud(construct_mud(connection), 6666)

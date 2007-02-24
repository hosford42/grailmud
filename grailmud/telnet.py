"""A couple of handy classes for the nitty-gritties of the telnet connection,
and keeping track of that sort of stuff.
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
from functional import compose
from hashlib import sha512 as sha
from twisted.conch.telnet import Telnet
from twisted.protocols.basic import LineOnlyReceiver
from grailmud.objects import Player, BadPassword, TargettableObject
from grailmud.actions import get_actions
from grailmud.actiondefs.logoff import logoffFinal
from grailmud.actiondefs.login import login
from grailmud.listeners import ConnectionState
from grailmud.strutils import sanitise, alphatise, safetise, articleise, \
                            wsnormalise
import grailmud

#some random vaguely related TODOs:
#-referential integrity when MUDObjects go POOF
#-this module could be split into two parts: the telnet protocol part, and the
#handlers part.

class LoggerIn(Telnet, LineOnlyReceiver):
    """A class that calls a specific method, depending on what the last method
    called returned.
    """

    delimiter = '\n'

    def __init__(self):
        Telnet.__init__(self)
        #LineOnlyReceiver doesn't have an __init__ method, weirdly.
        self.callback = lambda line: logging.debug("Doing nothing with %s" %
                                                   line)
        self.avatar = None
        self.connection_lost_callback = lambda: None

    applicationDataReceived = LineOnlyReceiver.dataReceived

    def lineReceived(self, line):
        """Receive a line of text and delegate it to the method asked for
        previously.
        """
        #XXX: turn this into a deferred thingy and have it disconnect on
        #errback.
        meth = self.callback
        logging.debug("Line %r received, putting %r for the ticker." %
                      (line, meth))
        grailmud.instance.ticker.add_command(lambda: meth(line))

    def close(self):
        """Convenience."""
        self.transport.loseConnection()

    def write(self, data):
        """Convenience."""
        logging.debug("Writing %r to the transport." % data)
        self.transport.write(data)

    def connectionMade(self):
        """The connection's been made, and send out the initial options."""
        Telnet.connectionMade(self)
        LineOnlyReceiver.connectionMade(self)
        ChoiceHandler(self).initial()

    def connectionLost(self, reason):
        """Clean up and let the superclass handle it."""
        if self.avatar:
            logoffFinal(self.avatar)
        self.connection_lost_callback()
        Telnet.connectionLost(self, reason)
        LineOnlyReceiver.connectionLost(self, reason)

class LineInfo(object):
    """A catch-all class for other useful information that needs to be handed
    to avatars with lines of commands.
    """

    def __init__(self, instigator = None): #XXX: probably other stuff to go
                                           #here too.
        self.instigator = instigator

class ConnectionHandler(object):

    def __init__(self, telnet):
        self.telnet = telnet

    def write(self, text):
        self.telnet.write(text)

    def setcallback(self, func):
        self.telnet.callback = func

NEW_CHARACTER = 1
LOGIN = 2

class NotAllowed(Exception):
    """The input was not acceptable, with an optional explanation."""

    def __init__(self, msg = "That input is invalid."):
        self.msg = msg

def toint(s):
    """Convert s to an int, or throw a NotAllowed."""
    try:
        return int(s)
    except ValueError:
        raise NotAllowed("That couldn't be parsed as a number.")

def strconstrained(blankallowed = False, corrector = sanitise,
                   msg = 'Try actually writing something usable?'):
    """Decorator to ensure that the function is only called with acceptable
    input.
    """
    def constrained(fn):
        def checker(self, line):
            logging.debug("Constraining input (%r) to %r" % (line, fn))
            try:
                line = corrector(line.lower())
            except NotAllowed, e:
                logging.debug("NotAllowed caught, writing %s" % e.msg)
                self.write(e.msg)
            else:
                if not blankallowed and not line:
                    self.write(msg)
                    return
                return fn(self, line)
        return checker
    return constrained

class ChoiceHandler(ConnectionHandler):

    def initial(self):
        self.write("Welcome to GrailMUD.\r\n")
        self.write("Please choose:\r\n")
        self.write("1) Enter the game with a new character.\r\n")
        self.write("2) Log in as an existing character.\r\n")
        self.write("Please enter the number of your choice.")
        self.setcallback(self.choice_made)

    #we want this here for normalisation purposes.
    @strconstrained(corrector = toint)
    def choice_made(self, opt):
        """The user's made their choice, so we pick the appropriate route: we
        either create a new character, or log in as an old one.
        """
        logging.debug("ChoiceHandler.choice_made called.")
        if opt == NEW_CHARACTER:
            self.successor = CreationHandler(self.telnet)
        elif opt == LOGIN:
            self.successor = LoginHandler(self.telnet)
        else:
            self.write("That is not a valid option.")

class CreationHandler(ConnectionHandler):

    #stop race conditions
    creating_right_now = set()

    def __init__(self, *args, **kwargs):
        self.name = None
        self.sdesc = None
        self.adjs = None
        self.passhash = None
        ConnectionHandler.__init__(self, *args, **kwargs)
        self.write("Enter your name.")
        self.setcallback(self.get_name)

    @strconstrained(corrector = alphatise)
    def get_name(self, name):
        """The user's creating a new character. We've been given the name,
        so we ask for the password.
        """
        name = name.lower()
        if name in TargettableObject._name_registry or \
           name in CreationHandler.creating_right_now:
            self.write("That name is taken. Please use another.")
        else:
            self.name = name
            CreationHandler.creating_right_now.add(name)
            self.write("Please enter a password for this character.")
            self.setcallback(self.get_password)
            self.telnet.connection_lost_callback = self.unlock_name

    def get_password(self, line):
        """We've been given the password. Hash it, then store the hash.
        """
        #XXX: probably ought to salt, too.
        line = safetise(line)
        if len(line) <= 3:
            self.write("That password is not long enough.")
            return
        self.passhash = sha(line).digest()
        self.write("Please repeat your password.")
        self.setcallback(self.repeat_password)

    def repeat_password(self, line):
        """Make sure the user can remember the password they've entered."""
        line = safetise(line)
        if sha(line).digest() != self.passhash:
            self.write("Those passwords don't match. Please enter a new one.")
            self.setcallback(self.get_password)
        else:
            self.write("Enter your description (eg, 'short fat elf').")
            self.setcallback(self.get_sdesc)

    @strconstrained(corrector = compose(sanitise, wsnormalise))
    def get_sdesc(self, line):
        """Got the sdesc; ask for the adjectives."""
        self.sdesc = articleise(line)
        self.write("Enter a comma-separated list of words that can be used to "
                   "refer to you (eg, 'hairy tall troll') or a blank line to "
                   "use your description.")
        self.setcallback(self.get_adjs)

    @strconstrained(blankallowed = True,
                    corrector = compose(alphatise, wsnormalise))
    def get_adjs(self, line):
        """Got the adjectives; create the avatar and insert the avatar into
        the game.
        """
        if not line:
            line = self.sdesc
        self.adjs = set(word.lower() for word in line.split())
        avatar = Player(self.name, self.sdesc, self.adjs, get_actions(),
                        grailmud.instance.startroom, self.passhash)
        self.unlock_name()
        self.successor = AvatarHandler(self.telnet, avatar)

    def unlock_name(self):
        """Remove our lock on the name, either because it's been created or
        because we lost the connection.
        """
        CreationHandler.creating_right_now.remove(self.name)
        self.telnet.connection_lost_callback = lambda: None

class LoginHandler(ConnectionHandler):

    def __init__(self, telnet):
        #XXX: what happens if a character is logged in twice?
        self.name = None
        ConnectionHandler.__init__(self, telnet)
        self.write("What is your name?")
        self.setcallback(self.get_name)
        
    @strconstrained(corrector = alphatise)
    def get_name(self, line):
        """Logging in as an existing character, we've been given the name. We
        ask for the password next.
        """
        line = line.lower()
        if Player.exists(line):
            self.name = line
            self.write("Please enter your password.\xff\xfa")
            self.setcallback(self.get_password)
        else:
            self.write("That name is not recognised. Please try again.")

    def get_password(self, line):
        """We've been given the password. Check that it's correct, and then
        insert the appropriate avatar into the MUD.
        """
        line = safetise(line)
        passhash = sha(line).digest()
        try:
            avatar = Player.get(line, passhash)
        except BadPassword, err:
            self.write("That password is invalid. Goodbye!")
            self.telnet.connectionLost(err)
        else:
            self.successor = AvatarHandler(self.telnet, avatar)

class AvatarHandler(ConnectionHandler):

    def __init__(self, telnet, avatar):
        self.telnet = telnet
        self.avatar = avatar
        
        self.connection_state = ConnectionState(self.telnet)
        self.avatar.addListener(self.connection_state)
        grailmud.instance.startroom.add(self.avatar)
        login(self.avatar)
        self.connection_state.eventListenFlush(self.avatar)
        self.setcallback(self.handle_line)

    @strconstrained(blankallowed = True,
                    corrector = safetise)
    def handle_line(self, line):
        logging.debug('%r received, handling in avatar.' % line)
        try:
            self.avatar.receivedLine(line,
                                     LineInfo(instigator = self.avatar))
            self.avatar.eventFlush()
        except:
            logging.error('Unhandled error %e, closing session.')
            logoffFinal(self.avatar)
            raise

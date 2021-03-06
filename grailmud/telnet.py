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
from grailmud.objects import Player, BadPassword, NamedObject
from grailmud.actions import get_actions
from grailmud.actiondefs.logoff import logoffFinal
from grailmud.actiondefs.login import login
from grailmud.delegates import ConnectionState
from grailmud.strutils import sanitise, alphatise, safetise, articleise, \
                            wsnormalise
import grailmud
from grailmud.nvt import make_string_sane
from functools import wraps
from grailmud.utils import defaultinstancevariable
from formencode import Invalid
from formencode.validators import NotEmpty, MinLength, MaxLength, Int,\
        FancyValidator, Wrapper
from formencode.compound import All
from string import lower

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
        line = make_string_sane(line)
        meth = self.callback
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

    def __eq__(self, other):
        return self.__dict__ == other.__dict__

class ConnectionHandler(object):

    def __init__(self, telnet):
        self.telnet = telnet

    def write(self, text):
        self.telnet.write(text)

    def setcallback(self, func):
        self.telnet.callback = func

NEW_CHARACTER = 1
LOGIN = 2

def validate_input(*validators):
    """Decorator to ensure that the function is only called with acceptable
    input.
    """
    validator = All(*validators)
    def constrainer(fn):
        @wraps(fn)
        def checker(self, line):
            logging.debug("Constraining input (%r) to %r" % (line, fn))
            try:
                res = validator.to_python(line)
            except Invalid, e:
                logging.debug("Invalid writing %s" % str(e))
                self.write(str(e))
            else:
                return fn(self, res)
        return checker
    return constrainer

class LowerCase(FancyValidator):

    def _to_python(self, value, state):
        return value.lower()

class ChoiceHandler(ConnectionHandler):

    def initial(self):
        self.write("Welcome to GrailMUD.\r\n")
        self.write("Please choose:\r\n")
        self.write("1) Enter the game with a new character.\r\n")
        self.write("2) Log in as an existing character.\r\n")
        self.write("Please enter the number of your choice.")
        self.setcallback(self.choice_made)

    #we want this here for normalisation purposes.
    @validate_input(Int())
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

@defaultinstancevariable(Player, "cmdict")
def default_cmdict(self):
    return get_actions()

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

    @validate_input(LowerCase(), Wrapper(to_python = alphatise), MinLength(3),
                    MaxLength(12))
    def get_name(self, name):
        """The user's creating a new character. We've been given the name,
        so we ask for the password.
        """
        if name in NamedObject._name_registry or \
           name in CreationHandler.creating_right_now:
            self.write("That name is taken. Please use another.")
        else:
            self.name = name
            CreationHandler.creating_right_now.add(name)
            self.write("Please enter a password for this character.")
            self.setcallback(self.get_password)
            self.telnet.connection_lost_callback = self.unlock_name

    @validate_input(Wrapper(to_python = safetise), MinLength(3))
    def get_password(self, line):
        """We've been given the password. Hash it, then store the hash.
        """
        #XXX: probably ought to salt, too.
        self.passhash = sha(line).digest()
        self.write("Please repeat your password.")
        self.setcallback(self.repeat_password)

    @validate_input(Wrapper(to_python = safetise))
    def repeat_password(self, line):
        """Make sure the user can remember the password they've entered."""
        if sha(line).digest() != self.passhash:
            self.write("Those passwords don't match. Please enter a new one.")
            self.setcallback(self.get_password)
        else:
            self.write("Enter your description (eg, 'short fat elf').")
            self.setcallback(self.get_sdesc)

    @validate_input(Wrapper(to_python = compose(sanitise, wsnormalise)), 
                    NotEmpty())
    def get_sdesc(self, line):
        """Got the sdesc; ask for the adjectives."""
        self.sdesc = articleise(line)
        self.write("Enter a comma-separated list of words that can be used to "
                   "refer to you (eg, 'hairy tall troll') or a blank line to "
                   "use your description.")
        self.setcallback(self.get_adjs)

    @validate_input(Wrapper(to_python = compose(alphatise, wsnormalise)))
    def get_adjs(self, line):
        """Got the adjectives; create the avatar and insert the avatar into
        the game.
        """
        if not line:
            line = self.sdesc
        #TODO: we want finer-grained control over who gets what command. While
        #the current method is convenient, it's not really the best.
        self.adjs = set(word.lower() for word in line.split())
        avatar = Player(self.name, self.sdesc, self.adjs,
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
        
    @validate_input(Wrapper(to_python = compose(alphatise, lower, 
                                                wsnormalise)))
    def get_name(self, line):
        """Logging in as an existing character, we've been given the name. We
        ask for the password next.
        """
        if Player.exists(line):
            self.name = line
            self.write("Please enter your password.\xff\xfa")
            self.setcallback(self.get_password)
        else:
            self.write("That name is not recognised. Please try again.")

    @validate_input(Wrapper(to_python = safetise))
    def get_password(self, line):
        """We've been given the password. Check that it's correct, and then
        insert the appropriate avatar into the MUD.
        """
        passhash = sha(line).digest()
        try:
            avatar = Player.get(self.name, passhash)
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
        self.avatar.addDelegate(self.connection_state)
        self.avatar.room.add(self.avatar)
        login(self.avatar)
        self.setcallback(self.handle_line)

    @validate_input(Wrapper(to_python = safetise))
    def handle_line(self, line):
        logging.debug('%r received, handling in avatar.' % line)
        try:
            self.avatar.receivedLine(line,
                                     LineInfo(instigator = self.avatar))
        except:
            logging.error('Unhandled error %e, closing session.')
            logoffFinal(self.avatar)
            raise

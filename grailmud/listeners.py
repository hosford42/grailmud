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
from grailmud.morelimiter import MoreLimiter
from grailmud.actiondefs.more import displayMore
from grailmud.objects import definein, Player

class Listener(object):
    '''Base class for listeners.'''

    _pickleme = True

    def __init__(self):
        self.listening = set()

    def register(self, source):
        """Register ourselves as a listener."""
        self.listening.add(source)

    def unregister(self, source):
        """Unregister ourselves as a listener."""
        self.listening.remove(source)

    def disconnecting(self, source):
        '''Acknowledge that an object has disconnected.'''
        source.removeListener(self)

    def transferControl(self, source, new):
        source.removeListener(self)
        new.addListener(self)

    def listenToEvent(self, obj, event):
        raise NotImplementedError()

@definein(Player._instance_variable_factories)
def more_limiter(self):
    return MoreLimiter(20)

@definein(Player._instance_variable_factories)
def chunks(self):
    return iter([])

@definein(Player._instance_variable_factories)
def chunked_event(self):
    return None

class ConnectionState(Listener):
    """Represents the state of the connection to the events as they collapse 
    to text."""

    _pickleme = False

    def __init__(self, telnet):
        self.telnet = self.target = telnet
        self.on_newline = False
        self.on_prompt = False
        self.want_prompt = True
        self.nonce = {}
        Listener.__init__(self)
        self.chunking = False

    def avatar_get(self):
        return self.telnet.avatar

    def avatar_set(self, new):
        self.telnet.avatar = new

    avatar = property(avatar_get, avatar_set)

    def sendIACGA(self):
        """Write an IAC GA (go-ahead) code to the telnet connection."""
        #self.telnet.write('\xFF\xFA')
        pass

    def chunk(self):
        """Chunkify our output."""
        self.chunking = True
        self.target = StringIO()

    def sendPrompt(self):
        """Send a prompt, plus an IAC GA (-without- a trailing newline)."""
        logging.debug("Sending a prompt.")
        self.forceNewline()
        self.target.write('-->')
        self.sendIACGA()
        self.on_prompt = True
        self.want_prompt = True
        self.on_newline = False

    def forcePrompt(self):
        """Ensure we are on a prompt. May be a noop."""
        if not self.on_prompt:
            self.sendPrompt()

    def sendEventLine(self, line):
        """Send a line, with \\r\\n appended."""
        self.sendEventData(line)
        self.forceNewline()

    def sendEventData(self, data):
        """Write a blob of data to the telnet connection. Sets self.on_prompt 
        to False, and on_newline to the appropriate value.
        """
        #TODO: when colours are implemented (itself a fairly major TODO), this
        #will have to check through the data for newlines and add in the 
        #current colour information if it is chunked, because otherwise it may
        #be lost.
        self.target.write(data)
        logging.debug("%r written." % data)
        self.on_prompt = False
        self.on_newline = False

    def dontWantPrompt(self):
        """We don't want a prompt next flush."""
        self.want_prompt = False

    def setColourName(self, colour):
        """Set our colour output to a predefined one."""
        pass #XXX

    def forceNewline(self):
        """Ensure we're on a newline."""
        if not self.on_newline:
            #see the note above, in sendEventData
            self.target.write('\r\n')
            self.on_newline = True

    def forcePromptNL(self):
        """Ensure we're on a prompt-newline."""
        self.forcePrompt()
        self.forceNewline()

    def listenToEvent(self, obj, event):
        """Collapse an event to text."""
        logging.debug("Handling event %r." % event)
        event.collapseToText(self, self.avatar)
        if self.chunking:
            bigchunk = self.target.getvalue()
            self.avatar.chunks = self.avatar.more_limiter.chunk(bigchunk)
            self.avatar.chunked_event = event
            self.chunking = False
            self.target = self.telnet
            displayMore(self.avatar)

    def eventListenFlush(self, obj):
        """Send off a final prompt to finish off the events."""
        logging.debug("Flushing the events, and stuff.")
        if self.want_prompt:
            self.sendPrompt()
        self.want_prompt = True
        self.nonce = {}

    def disconnecting(self, obj):
        if obj is self.avatar:
            #our avatar is disconnecting: we need to tell our telnet to close.
            #self.listening may be mutated by the listenees removal
            for listening_to in self.listening.copy():
                listening_to.removeListener(self)
            logging.debug("Disconnecting the telnet instance.")
            self.telnet.close()
        else:
            #this is in an else block because this implies a call to
            #the removeListener of our avatar, which would blow up.
            Listener.disconnecting(self, obj)

    def transferControl(self, source, other):
        if source is self.avatar:
            self.avatar = other
        Listener.transferControl(self, source, other)

"""A Python MUD."""

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

#instance is the currently running MUD instance, or None. Either we'd have to 
#do some attribute trickery here, or you can only have one instance per Python
#interpreter.
class _LateProxy(object):
    '''An attribute forwarder that can be bound 'late' or not at initialisation
    time.
    '''

    def __init__(self):
        self._bound = False
        self._boundto = None

    def __getattr__(self, name):
        if self._bound:
            return getattr(self._boundto, name)
        raise ValueError("Not bound yet!")

    def _bind(self, obj):
        '''Bind the proxy to an object.'''
        self._bound = True
        self._boundto = obj

instance = _LateProxy()

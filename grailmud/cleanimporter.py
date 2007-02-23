__copyright__ = """Copyright 2007 Sam Pointon."""

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

import sys

def fetch_module_and_names(modname):
    mod = __import__(modname)
    components = modname.split('.')[1:]
    try:
        for comp in components:
            mod = getattr(mod, comp)
    except AttributeError:
        raise ImportError()
    if hasattr(mod, '__all__'):
        names = mod.__all__
    else:
        names = [name for name in dir(mod) if name[0] != '_']
    return mod, names
    

class CleanImporter(object):
    #this does NOT clobber local names if used inside a function, and in fact
    #leaves locals well alone. This may be a problem when coupled with the
    #compiler's sneaky optimisation of local versus global lookup: names not
    #assigned to in a local are assumed to be global, which directly influences
    #this module's operation.

    def __init__(self, modname):
        self.modname = modname
        self.oldglobals = {}
        self.names = None

    def __enter__(self):
        mod, self.names = fetch_module_and_names(self.modname)
        
        self.frame = sys._getframe(1)

        for name in self.names:
            if name in self.frame.f_globals:
                self.oldglobals[name] = self.frame.f_globals[name]
            val = getattr(mod, name)
            self.frame.f_globals[name] = val

    def __exit__(self, typ, val, tb):
        for name in self.names:
            del self.frame.f_globals[name]
        self.frame.f_globals.update(self.oldglobals)

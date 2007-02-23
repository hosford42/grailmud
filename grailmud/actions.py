'''Pulls the actions from the definitions files underneath actiondefs.'''

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

from collections import defaultdict
import pkg_resources

modulenames = []

for filename in pkg_resources.resource_listdir(__name__, 'actiondefs'):
    package = pkg_resources.resource_exists(__name__, 'actiondefs/' + filename)
    if filename.endswith('py'):
        module = True
        filename = filename[:-3]
    else:
        module = False
    if module or package:
        modulenames.append(filename)

m = __import__('grailmud.actiondefs', fromlist = modulenames)
modules = [getattr(m, name) for name in modulenames]

def get_actions():
    '''Goes over all the actiondef modules and registers the cdict.'''
    cdict = defaultdict()
    for module in modules:
        if hasattr(module, "register"):
            module.register(cdict)
    return cdict

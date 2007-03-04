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

import re

toremove = set('\000' #NUL
               '\007' #BEL
               '\011' #HT
               '\013' #VT
               '\014') #FF

BS = '\010'

def make_string_sane(string):
    for char in toremove:
        string = string.replace(char, '')
    string = string.lstrip(BS)
    while BS in string:
        print string
        string = re.sub('.' + BS, '', string, 1)
        print string
    return string



"""This module contains a tool for emulating a network virtual terminal. See
RFC 854 for details.
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

import re

toremove = set('\000' #NUL
               '\007' #BEL
               '\011' #HT
               '\013' #VT
               '\014') #FF

BS = '\010'

def make_string_sane(string):
    """Process (in most cases, this means 'ignore') the NVT characters in the
    input string.
    """
    #simple characters don't need any special machinery.
    for char in toremove:
        string = string.replace(char, '')
    #do it backspace by backspace because otherwise, if there were multiple 
    #backspaces in a row, it gets confused and backspaces over backspaces.
    while BS in string:
        #take off leading backspaces so that the following regex doesn't get 
        #confused.
        string = string.lstrip(BS)
        string = re.sub('.' + BS, '', string, 1)
    return string



from __future__ import with_statement

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

from string import printable, whitespace, ascii_letters, digits, punctuation
from grailmud.cleanimporter import CleanImporter

#I don't know either, but some modules want this
printables = printable

nwprintable = ''.join(s for s in printable if s not in whitespace)

alnumspace = ascii_letters + digits + whitespace

def sanitise(string):
    """Strip non-alphabetic/space chars from the string."""
    return ''.join(s for s in string if s.isalpha() or s == ' ')

def alphatise(string):
    """strip non-alphabetic chars from string."""
    return ''.join(s for s in string if s.isalpha())

def safetise(string):
    """strip non-printable chars from the string"""
    return ''.join(s for s in string if s in printable)

def articleise(string):
    """Append the appropriate indefinite article to the string."""
    if string[0] in 'aeiou':
        return 'an ' + string
    return 'a ' + string

def capitalise(s):
    """Capitalise in BrE."""
    #we do it -better- than s.capitalize() - that lowercases the rest.
    if not s:
        #don't blow up on the empty string - otherwise we get IndexError
        return ''
    return s[0].upper() + s[1:]

#it takes prefixes of symbols to be the 'head word'.
with CleanImporter('pyparsing'):
    # pylint: disable-msg=E0602
    _hwspattern = (Word(punctuation) + Optional(Word(alnumspace))) ^ \
                  (Optional(Word(nwprintable)) + Optional(Word(printable)))

#XXX: tabs. watch it blow up!

def head_word_split(string):
    """Split off the first word or group of non-whitespace punctuation."""
    res = _hwspattern.parseString(string)
    if len(res) == 0:
        return ('', '')
    elif len(res) == 1:
        return (res[0], '')
    else:
        return tuple(res)

def wsnormalise(string):
    """Normalise the whitespace to just one space per blob of it."""
    return ' '.join(s for s in string.split() if s)

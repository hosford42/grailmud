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

from grailmud.cleanimporter import CleanImporter
import string

def test_imported_names():
    with CleanImporter('string'):
        assert string.punctuation == punctuation
        assert string.capitalize == capitalize
        assert string.digits == digits

def test_cleanup():
    before = len(globals())
    with CleanImporter("string"):
        #this test is important: it makes sure this isn't a no-op
        assert len(globals()) != before
    assert len(globals()) == before

def test_no_clobbering():
    #need to do this because CleanImporter only adds it to the global scope.
    s = '''
punctuation = 'foo'
with CleanImporter("string"):
    assert string.punctuation == punctuation, punctuation
assert punctuation == 'foo', punctuation
'''
    exec s in globals()

#XXX: some tests for the import reimplementation.

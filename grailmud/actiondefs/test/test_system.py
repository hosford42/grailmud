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

from grailmud.actiondefs.system import UnfoundObjectEvent, PermissionDeniedEvent,\
                                     BadSyntaxEvent, BlankLineEvent, blankLine,\
                                     permissionDenied, badSyntax, \
                                     unfoundObject, register
from grailmud.utils_for_testing import SetupHelper

def test_registration():
    d = {}
    register(d)
    assert d[''] is blankLine

class TestEvents(SetupHelper):

    def test_bad_syntax_without_argument(self):
        badSyntax(self.obj)
        assert self.obj.listener.received == [BadSyntaxEvent(None)]

    def test_bad_syntax_with_argument(self):
        arg = "foo"
        badSyntax(self.obj, arg)
        assert self.obj.listener.received == [BadSyntaxEvent(arg)]

    def test_blank_line(self):
        blankLine(self.obj, "foo", None)
        assert self.obj.listener.received == [BlankLineEvent()]

    def test_permission_denied(self):
        permissionDenied(self.obj)
        assert self.obj.listener.received == [PermissionDeniedEvent()]

def test_BadSyntaxEvent_equality():
    a = BadSyntaxEvent("foo")
    b = BadSyntaxEvent("bar")
    assert a == b

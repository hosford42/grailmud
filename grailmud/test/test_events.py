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

from grailmud.events import *

class MyVeryOwnEvent(BaseEvent):
    pass

def test_subclasses():
    assert issubclass(SystemEvent, BaseEvent)
    assert issubclass(GameEvent, BaseEvent)
    assert issubclass(VisibleEvent, BaseEvent)
    assert issubclass(AudibleEvent, BaseEvent)

def test_equality():
    a = MyVeryOwnEvent()
    b = MyVeryOwnEvent()
    assert a == b
    a.foo = "bar"
    assert a != b
    b.foo = "bar"
    assert a == b

def test_not_implemented_collapseToText():
    try:
        BaseEvent().collapseToText(None, None)
    except NotImplementedError:
        pass
    else:
        assert False

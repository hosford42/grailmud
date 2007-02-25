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

from grailmud.ticks import Ticker
import pickle
import grailmud

def test_ticker_freq_setting():
    interval = 0.5
    t = Ticker(interval)
    assert t.freq == interval

def test_command_added():
    t = Ticker(1)
    #hackish
    called = []
    t.add_command(lambda: called.append(True))
    t.tick()
    assert called

def test_clears_doing_list():
    def doing_list_checker():
        assert not ticker.doing

    ticker = Ticker(1)
    ticker.add_command(doing_list_checker)
    ticker.tick()

def test_frequency_persists():
    freq = 1
    t = Ticker(freq)
    t = pickle.loads(pickle.dumps(t))
    assert t.freq == freq

def foo_function_1():
    pass

def foo_function_2():
    pass

def test_doing_persists():
    t = Ticker(1)
    t.add_command(foo_function_1)
    t.add_command(foo_function_2)
    olddoing = t.doing
    t = pickle.loads(pickle.dumps(t))
    assert t.doing == olddoing

class MockObjStore(object):

    def commit(self):
        pass

class MockInstance(object):

    def __init__(self):
        self.objstore = MockObjStore()

grailmud.instance._bind(MockInstance())

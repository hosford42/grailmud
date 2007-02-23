__copyright__ = """Adapted from test_set.py in the test suite, copyright the
Python Software Foundation, by Sam Pointon, 2007."""

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
#NOTE: if you change these imports, don't forget to delete them at the end!
from test.test_set import TestSet as BuiltinSet, \
                          TestBinaryOps as BuiltinBinaryOps, \
                          TestUpdateOps as BuiltinUpdateOps, \
                          TestMutate as BuiltinMutate 
from grailmud.orderedset import OSet
import unittest
from test import test_support
from weakref import proxy
import operator
import copy
import pickle
import os
from random import randrange, shuffle
import sys

empty_set = set()

def baditer():
    raise TypeError
    yield True

def gooditer():
    yield True

class PassThru(Exception):
    pass

def check_pass_thru():
    raise PassThru
    yield 1

class TestOrderedSet(BuiltinSet):

    thetype = OSet

    def test_difference(self):
        i = self.s.difference(self.otherword)
        for c in self.letters:
            self.assertEqual(c in i, c in self.d and c not in self.otherword)
        self.assertEqual(self.s, self.thetype(self.word))
        self.assertEqual(type(i), self.thetype)
        self.assertRaises(PassThru, self.s.difference, check_pass_thru())
#        self.assertRaises(TypeError, self.s.difference, [[]])
        for C in set, frozenset, dict.fromkeys, str, unicode, list, tuple:
            self.assertEqual(self.thetype('abcba').difference(C('cdc')), set('ab'))
            self.assertEqual(self.thetype('abcba').difference(C('efgfe')), set('abc'))
            self.assertEqual(self.thetype('abcba').difference(C('ccb')), set('a'))
            self.assertEqual(self.thetype('abcba').difference(C('ef')), set('abc'))

    def test_difference_update(self):
        retval = self.s.difference_update(self.otherword)
        self.assertEqual(retval, None)
        for c in (self.word + self.otherword):
            if c in self.word and c not in self.otherword:
                self.assert_(c in self.s)
            else:
                self.assert_(c not in self.s)
        self.assertRaises(PassThru, self.s.difference_update, check_pass_thru())
#        self.assertRaises(TypeError, self.s.difference_update, [[]])
#        self.assertRaises(TypeError, self.s.symmetric_difference_update, [[]])
        for p, q in (('cdc', 'ab'), ('efgfe', 'abc'), ('ccb', 'a'), ('ef', 'abc')):
            for C in set, frozenset, dict.fromkeys, str, unicode, list, tuple:
                s = self.thetype('abcba')
                self.assertEqual(s.difference_update(C(p)), None)
                self.assertEqual(s, set(q))

    def test_compare(self):
        pass

    def test_contains(self):
        for c in self.letters:
            self.assertEqual(c in self.s, c in self.d)
        self.assertRaises(TypeError, self.s.__contains__, [[]])
#        s = self.thetype([frozenset(self.letters)])
#        self.assert_(self.thetype(self.letters) in s)

    def test_discard(self):
        self.s.discard('a')
        self.assert_('a' not in self.s)
        self.s.discard('Q')
        self.assertRaises(TypeError, self.s.discard, [])
#        s = self.thetype([frozenset(self.word)])
#        self.assert_(self.thetype(self.word) in s)
#        s.discard(self.thetype(self.word))
#        self.assert_(self.thetype(self.word) not in s)
#        s.discard(self.thetype(self.word))

    def test_remove(self):
        self.s.remove('a')
        self.assert_('a' not in self.s)
        self.assertRaises(KeyError, self.s.remove, 'Q')
        self.assertRaises(TypeError, self.s.remove, [])
#        s = self.thetype([frozenset(self.word)])
#        self.assert_(self.thetype(self.word) in s)
#        s.remove(self.thetype(self.word))
#        self.assert_(self.thetype(self.word) not in s)
#        self.assertRaises(KeyError, self.s.remove, self.thetype(self.word))

class BasicOpsHelper(object):

    def test_repr(self):
        if self.repr is not None:
            self.assertEqual(repr(self.set), self.repr)

    def test_print(self):
        try:
            fo = open(test_support.TESTFN, "wb")
            print >> fo, self.set,
            fo.close()
            fo = open(test_support.TESTFN, "rb")
            self.assertEqual(fo.read(), repr(self.set))
        finally:
            fo.close()
            os.remove(test_support.TESTFN)

    def test_length(self):
        self.assertEqual(len(self.set), self.length)

    def test_self_equality(self):
        self.assertEqual(self.set, self.set)

    def test_equivalent_equality(self):
        self.assertEqual(self.set, self.dup)

    def test_copy(self):
        self.assertEqual(self.set.copy(), self.dup)

    def test_self_union(self):
        result = self.set | self.set
        self.assertEqual(result, self.dup)

    def test_empty_union(self):
        result = self.set | empty_set
        self.assertEqual(result, self.dup)

    def test_union_empty(self):
        result = empty_set | self.set
        self.assertEqual(result, self.dup)

    def test_self_intersection(self):
        result = self.set & self.set
        self.assertEqual(result, self.dup)

    def test_empty_intersection(self):
        result = self.set & empty_set
        self.assertEqual(result, empty_set)

    def test_intersection_empty(self):
        result = empty_set & self.set
        self.assertEqual(result, empty_set)

    def test_self_symmetric_difference(self):
        result = self.set ^ self.set
        self.assertEqual(result, empty_set)

    def checkempty_symmetric_difference(self):
        result = self.set ^ empty_set
        self.assertEqual(result, self.set)

    def test_self_difference(self):
        result = self.set - self.set
        self.assertEqual(result, empty_set)

    def test_empty_difference(self):
        result = self.set - empty_set
        self.assertEqual(result, self.dup)

    def test_empty_difference_rev(self):
        result = empty_set - self.set
        self.assertEqual(result, empty_set)

    def test_iteration(self):
        for v in self.set:
            self.assert_(v in self.values)
        setiter = iter(self.set)
        # note: __length_hint__ is an internal undocumented API,
        # don't rely on it in your own programs
        self.assertEqual(setiter.__length_hint__(), len(self.set))

    def test_pickling(self):
        p = pickle.dumps(self.set)
        copy = pickle.loads(p)
        self.assertEqual(self.set, copy,
                         "%s != %s" % (self.set, copy))

class TestBasicOpsEmpty(BasicOpsHelper, unittest.TestCase):

    def setUp(self):
        self.case = 'empty ordered set'
        self.values = []
        self.set = OSet(self.values)
        self.dup = OSet(self.values)
        self.length = 0
        self.repr = 'OrderedSet([])'

class TestBasicOpsSingleton(BasicOpsHelper, unittest.TestCase):
    def setUp(self):
        self.case   = "unit ordered set (number)"
        self.values = [3]
        self.set    = OSet(self.values)
        self.dup    = OSet(self.values)
        self.length = 1
        self.repr   = "OrderedSet([3])"

    def test_in(self):
        self.failUnless(3 in self.set)

    def test_not_in(self):
        self.failUnless(2 not in self.set)

class TestBasicOpsTuple(BasicOpsHelper, unittest.TestCase):
    def setUp(self):
        self.case   = "unit ordered set (tuple)"
        self.values = [(0, "zero")]
        self.set    = OSet(self.values)
        self.dup    = OSet(self.values)
        self.length = 1
        self.repr   = "OrderedSet([(0, 'zero')])"

    def test_in(self):
        self.failUnless((0, "zero") in self.set)

    def test_not_in(self):
        self.failUnless(9 not in self.set)

class TestBasicOpsTriple(BasicOpsHelper, unittest.TestCase):
    def setUp(self):
        self.case   = "triple ordered set"
        self.values = [0, "zero", operator.add]
        self.set    = OSet(self.values)
        self.dup    = OSet(self.values)
        self.length = 3
        self.repr   = None

class TestExceptionPropagation(unittest.TestCase):
    """SF 628246:  Set constructor should not trap iterator TypeErrors"""

    def setUp(self):
        self.thetype = OSet

    def test_instanceWithException(self):
        self.assertRaises(TypeError, self.thetype, baditer())

    def test_instancesWithoutException(self):
        # All of these iterables should load without exception.
        self.thetype([1,2,3])
        self.thetype((1,2,3))
        self.thetype({'one':1, 'two':2, 'three':3})
        self.thetype(xrange(3))
        self.thetype('abc')
        self.thetype(gooditer())

#this is disabled because it works for lists. possibly this is wrong, but I'm
#going to disable it anyway.
#    def test_changingSizeWhileIterating(self):
#        s = self.thetype([1,2,3])
#        try:
#            for i in s:
#                s.update([4])
#        except RuntimeError:
#            pass
#        else:
#            self.fail("no exception when changing size during iteration")

class TestSetOfSets(unittest.TestCase):
    def test_constructor(self):
        inner = frozenset([1])
        outer = OSet([inner])
        element = outer.pop()
        self.assertEqual(type(element), frozenset)
        outer.add(inner)        # Rebuild set of sets with .add method
        outer.remove(inner)
        self.assertEqual(outer, OSet())   # Verify that remove worked
        outer.discard(inner)    # Absence of KeyError indicates working fine

class TestBinaryOps(BuiltinBinaryOps):
    #XXX: what's test_cmp meant to be doing?

    def setUp(self):
        self.set = OSet((2, 4, 6))

class TestUpdateOps(BuiltinUpdateOps):

    def setUp(self):
        self.set = OSet((2, 4, 6))

class TestMutate(BuiltinMutate):

    def setUp(self):
        self.values = ["a", "b", "c"]
        self.set = OSet(self.values)

    def test_add_until_full(self):
        tmp = set()
        expected_len = 0
        for v in self.values:
            tmp.add(v)
            expected_len += 1
            self.assertEqual(len(tmp), expected_len)
        self.assertEqual(self.set, tmp)

#XXX: I've got as far as TestSubset.

#we need to delete these names else nose will pick them up as subclasses of
#unittest.UnitTest (or whatever they are) and run them, which is rather less
#than pointful.
del BuiltinSet
del BuiltinBinaryOps
del BuiltinUpdateOps
del BuiltinMutate

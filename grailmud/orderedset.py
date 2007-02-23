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

from sets import BaseSet
from functional import flip

_set_types = (set, frozenset, BaseSet)

def _operand_set_checking(fn):
    '''Ensure that the other operand is a set.'''
    def func(self, other):
        if not isinstance(other, _set_types):
            return NotImplemented
        res = fn(self, other)
        if res is None:
            return self
        return res
    return func

class OrderedSet(list):
    '''A collection of unique elements, kept in order. Mutable.'''
    #Possibly todo: write an immutable ordered set? Inheriting from tuple?
    
    def __init__(self, seq = ()):
        list.__init__(self)
        self.extend(seq)

    _overwrite = list.__init__

    def __contains__(self, item):
        hash(item)
        return list.__contains__(self, item)

    def __repr__(self):
        return '%s(%s)' % (type(self).__name__, list.__repr__(self))

    def __setslice__(self, i, j, sequence):
        self.__setitem__(slice(i, j), sequence)

    def __setitem__(self, key, value):
        if isinstance(key, slice):
            res = self.intersection(value)
        else:
            res = value in self
        if res:
            raise ValueError('Item is already a member.')
        list.__setitem__(self, key, value)

    def __getitem__(self, key):
        res = list.__getitem__(self, key)
        if isinstance(key, slice):
            return OrderedSet(res)
        return res

    def __getslice__(self, i, j):
        return self.__getitem__(slice(i, j))

    #List methods, suitably wrapped and checked.

    def append(self, item):
        '''Append an element to the end of the ordered set.

        Quietly returns if it is already a member.
        '''
        hash(item)
        if item in self:
            #raise ValueError("Item is already a member.")
            return #silently ignore.
                   #XXX: strict option?
        list.append(self, item)

    def count(self, value):
        '''Return the number of times an element occurs.

        Due to the very nature of sets, this will either be 0 or 1.
        '''
        return int(value in self)

    def extend(self, values):
        '''Extend the ordered set with a sequence of elements.

        This preserves the order of the elements. Duplicates are silently
        ignored.
        '''
        appending = []
        for value in values:
            hash(value)
            appending.append(value)

        for value in appending:
            self.add(value)

    def insert(self, key, value):
        '''Set a given index to a value.

        Raises a ValueError if the element is already a member.
        '''
        #why not just self[key] = value?
        hash(value)
        self[key:key] = value

    #methods for frozenset compatability.

    #These two could be done using itertools.imap and the boolean operations.
    def issubset(self, other):
        '''Returns True if a given set is a subset of the ordered set.'''
        #don't blow up with generators
        other = list(other)
        if len(self) > len(other):
            return False
        for elem in self:
            if elem not in other:
                return False
        return True

    def issuperset(self, other):
        '''Returns True if a given set is a superset of the ordered set.'''
        #don't blow up with generators
        other = list(other)
        if len(self) < len(other):
            return False
        for elem in other:
            if elem not in self:
                return False
        return True

    def union(self, other):
        '''Return an OrderedSet of elements in both operands.'''
        res = OrderedSet(self)
        res.extend(other)
        return res

    def intersection(self, other):
        '''Return an OrderedSet of elements common to both operands.'''
        res = OrderedSet()
        other = list(other)
        if len(self) > len(other):
            #speed: this check is not needed other than to minimise the number
            #of iterations.
            other, self = self, other
        for elem in self:
            if elem in other:
                res.add(elem)
        return res

    def difference(self, other):
        '''Return the elements that do not appear in the other operand which do
        appear in this one.
        '''
        res = OrderedSet()
        other = list(other)
        for elem in self:
            if elem not in other:
                res.add(elem)
        return res

    def symmetric_difference(self, other):
        '''Return the elements that appear in one operand but not the other.'''
        res = self.difference(other)
        for elem in other:
            if elem not in self:
                res.add(elem)
        return res

    def copy(self):
        '''Return a new OrderedSet with the same elements.

        The elements are not copied.
        '''
        return OrderedSet(self)
    __copy__ = copy

    #Set methods.
    update = extend

    def intersection_update(self, other):
        '''Overwrite this OrderedSet with the operands' intersection.'''
        self._overwrite(self.intersection(other))

    def difference_update(self, other):
        '''Overwrite this OrderedSet instance with the operands' assymetric
        difference.
        '''
        self._overwrite(self.difference(other))

    def symmetric_difference_update(self, other):
        '''Overwrite this OrderedSet instance with the operands' symmetric
        difference.
        '''
        self._overwrite(self.symmetric_difference(other))
        
    def add(self, elem):
        '''Add an element to the OrderedSet, at the end.'''
        hash(elem)
        if elem not in self:
            list.append(self, elem)

    #remove is already implemented in the list inheritance: it'll raise the
    #wrong error, though (ValueError instead of KeyError). So we must wrap it,
    #making sure the error raised can be caught by ValueError and KeyError.
    def remove(self, elem):
        '''Remove an element from the OrderedSet, raising an error if the
        element is not present.
        '''
        hash(elem)
        try:
            list.remove(self, elem)
        except ValueError:
            raise DualValueError()

    def discard(self, elem):
        '''Remove an element from the OrderedSet quietly.'''
        if elem in self:
            self.remove(elem)

    #ditto as for remove, but we can do some dispatching. Thanks to Python's
    #amazing consistency, we have to raise a different error here: lists
    #throw a ValueError in remove but an IndexError in pop.
    def pop(self, index = None):
        '''Remove an object at a given index from the OrderedSet, or at the end
        if not specified.
        '''
        if index is None:
            #if index is None, it might be a set method, so the error raised
            #must be caught by "except IndexError" and "except KeyError".
            try:
                return list.pop(self, -1)
            except IndexError:
                raise DualError()
        else:
            #if not, it's a list thing: IndexError is expected, and list.pop
            #will raise that anyway.
            return list.pop(self, index)

    __or__ = _operand_set_checking(union)
    __ror__ = _operand_set_checking(flip(union))
    __and__ = _operand_set_checking(intersection)
    __rand__ = _operand_set_checking(flip(intersection))
    __sub__ = _operand_set_checking(difference)
    __rsub__ = _operand_set_checking(flip(difference))
    __xor__ = _operand_set_checking(symmetric_difference)
    __rxor__ = _operand_set_checking(flip(symmetric_difference))
    __ior__ = _operand_set_checking(update)
    __iand__ = _operand_set_checking(intersection_update)
    __isub__ = _operand_set_checking(difference_update)
    __ixor__ = _operand_set_checking(symmetric_difference_update)

    def clear(self):
        '''Remove all elements from the instance.'''
        self._overwrite([])

    #Comparisons are difficult, as sets and lists do wildly different things.
    #Since the list comparisons are undefined in the library reference, AFAIK,
    #and the set ones are, those are what OrderedSets will support.
    
    #Should equality just test for membership (ie, set-style), or should
    #position count as well (list-style)? Of course, I could always do
    #dispatching to sniff out sets and compare them according to set rules, and
    #then use the list style on everything else.
    #The problem here is that __eq__ is overloaded, with two fundamentally
    #different operations. What would be more handy is two wholly separate
    #comparison functions. Then, code writers could pick and choose.

    def __lt__(self, other):
        if len(self) >= len(other):
            return False
        return self.issubset(other)

    __ge__ = issuperset

    def __gt__(self, other):
        if len(self) <= len(other):
            return False
        return self.issuperset(other)

    __le__ = issubset

    def __eq__(self, other):
        if isinstance(other, _set_types):
            return self.setcompare(other)
        else:
            return self.listcompare(other)

    listcompare = list.__eq__

    #we can't convert to set because we might have unhashable elements.
    #This assumes that neither operand will have non-unique elements.
    #obviously, we can't have non-unique elements, but they might.
    def setcompare(self, other):
        '''Compare the OrderedSet to another set type as a set.'''
        return not self.symmetric_difference(other)

    def __ne__(self, other):
        return not (self == other)

    #my convenience methods.
    def rmapp(self, elem):
        '''Remove an element from the OrderedSet if it is present, then place
        it at the end.
        '''
        try:
            self.remove(elem)
        except IndexError:
            pass
        self.append(elem)


class DualError(KeyError, IndexError):
    """An error that can be caught by both 'KeyError' and 'IndexError'"""
    pass

class DualValueError(KeyError, ValueError):
    """An error that can be caught by both 'KeyError' and 'ValueError'"""
    pass

OSet = OrderedSet

_set_types += (OSet,)

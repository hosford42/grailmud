'''Type-based multimethods, with support for call-next-method functionality.
'''

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

import bisect
from functional import partial, flip
from grailmud.orderedset import OrderedSet

class Not(object):
    '''A type's complement.'''

    def __init__(self, typ):
        self.typ = typ

class Union(object):
    '''The union of several types.'''

    def __init__(self, *types):
        self.types = types

class Intersection(object):
    '''The intersection of several types.'''

    def __init__(self, *types):
        self.types = types

def complement(a, b):
    '''The difference of two types.'''
    return Intersection(a, Not(b))

def _cooler_issubclass(child, parent):
    '''An issubclass that's aware of the above classes.'''
    #typically, where multimethods would be a boon, we can't use them because
    #we have to bootstrap.
    if isinstance(parent, tuple):
        parent = Union(*parent)
    if isinstance(parent, Not):
        #pylint: disable-msg= E1103
        #pylint's type inference chokes on the next line.
        return not _cooler_issubclass(child, parent.typ)
        #pylint: enable-msg= E1103
    if isinstance(parent, Union):
        return any(_cooler_issubclass(child, typ) for typ in parent.types)
    if isinstance(parent, Intersection):
        return all(_cooler_issubclass(child, typ) for typ in parent.types)
    return issubclass(child, parent)

class Signature(object):
    '''A Signature of types for a function. Can be ordered, though it's only a
    partial ordering.
    '''

    def __init__(self, tsig):
        #Explicitly convert to tuple to prevent Bad Things from happening with
        #generator expressions.
        self.tsig = tuple(tsig)
    
    def supertypes(self, other):
        '''Returns True if our types supertype or are equal to the operand's
        types.
        '''
        if self.tsig == other.tsig:
            return True
        return self.strict_supertypes(other)

    def strict_supertypes(self, other):
        '''Returns True if all of our types supertype the operand's types.
        
        This also returns True if only some do, and the rest are equal.
        '''
        if len(self.tsig) != len(other.tsig):
            return False

        if self.tsig == other.tsig:
            return False
        
        zipped_types = zip(self.tsig, other.tsig)
        #Is it just me, or is the argument order for issubclass completely
        #arbitrary? I've tripped up on that so many times - my preferred 
        #method of turning it into a Haskell style infix thingy and then 
        #reading it aloud ("b `issubclass` a") doesn't help. I think it ought 
        #to be renamed 'issubclassof' and the argument order reversed.
        if all(_cooler_issubclass(theirs, ours) 
               for ours, theirs in zipped_types):
            return True

        return False

    __ge__ = supertypes
    __le__ = flip(supertypes)
    __gt__ = strict_supertypes
    __lt__ = flip(strict_supertypes)

    def __repr__(self):
        return "Signature%s" % repr(self.tsig)

    def __hash__(self):
        return hash(self.tsig)

    def __eq__(self, other):
        return self.tsig == other.tsig

class Multimethod(object):
    '''A function that can dispatch based on the types of all its arguments, 
    not just the first one, like it is traditionally.
    '''

    def __init__(self):
        self.signatures = OrderedSet()
        self.s2fs = {}
        self.next_method_stack = []

    def register(self, *sig):
        '''Takes a signature of types, and returns a function that takes a
        function, which registers the given function to the internal machinery
        with the signature.
        '''
        sig = Signature(sig)
        def functiongrabber(func):
            #The magic is actually done here: self.signatures is always in
            #sorted order, so that when we iterate through it it's just a
            #matter of checking if the signature matches or not. Of course,
            #this means we need to -maintain- sorted order, so bisect.insort
            #is used to do the algorithmic lifting.
            if sig not in self.signatures:
                #If it's already in there, it'll be at the correct index.
                bisect.insort_right(self.signatures, sig)
                #but, its signature won't be in the s2fs dict if it's not
                self.s2fs[sig] = []
            self.s2fs[sig].append(func)
            return self
        return functiongrabber

    def registermany(self, *sigs):
        """Register several signatures for a function at once."""
        def functiongrabber(func):
            for sig in sigs:
                self.register(sig)(func)
            return self
        return functiongrabber

    def __call__(self, *args):
        sig = Signature(type(arg) for arg in args)
        self.next_method_stack.append(self._get_functions(sig))
        try:
            return self._get_next_method(sig)(*args)
        finally:
            #dynamic scoping ... *cringe* ... but without resumable exceptions,
            #this is about the best we can do, alongside sticking a big fat
            #warning about its deficiencies somewhere.
            del self.next_method_stack[-1]

    def __get__(self, instance, owner):
        #Support for being used as a bound method.
        if instance is None:
            return self
        else:
            return partial(self, instance)

    def _fail(self, sig):
        '''This is called when there's no matching type signature. Please, do
        override this.
        '''
        raise TypeError("No matching signature was found for %r." %
                        sig)

    def _get_next_method(self, csig, noisy = True):
        '''Gets the next method from the stack of Signature-yielding iterables.
        '''
        try:
            return self.next_method_stack[-1].next()
        except StopIteration:
            if noisy:
                self._fail(csig)

    def _get_functions(self, csig):
        """Construct an iterator over all the matching functions for the given
        signature.
        """
        #Here comes the clever bit: self.signatures is stored in a sorted 
        #order, going from most to least specific type signatures, so we can 
        #simply iterate through it comparing our signature with its elements 
        #and use the functions whose signatures match. The beauty of using a 
        #generator for this is that we can be lazy about it.
        for sig in self.signatures:
            if sig.supertypes(csig):
                for func in self.s2fs[sig]:
                    yield func

    def call_next_method(self, *args):
        '''Calls the next method down from the present one. Throws an error
        if it doesn't have a next method.
        '''
        return self._call_next_method_helper(args, True)

    def call_next_method_quiet(self, *args):
        '''Like call_next_method, but it doesn't throw.'''
        return self._call_next_method_helper(args, False)

    def _call_next_method_helper(self, args, noisy):
        sig = Signature(type(arg) for arg in args)
        if not self.next_method_stack:
            raise ValueError("Don't call this outside of a call to a "
                             "multimethod.")
        meth = self._get_next_method(sig, noisy)
        return meth(*args)

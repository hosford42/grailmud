from __future__ import absolute_import
# pylint: disable-msg= E1101
#pylint doesn't know about our metaclass hackery

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

import logging
from grailmud.orderedset import OSet

def promptcolour(colourname = 'normal', chunk = False):
    """Eliminate some boilerplace for event text collapsers."""
    def fngrabber(func):
        def doer_of_stuff(self, state, obj):
            state.forcePrompt()
            if chunk:
                state.chunk()
            state.setColourName(colourname)
            func(self, state, obj)
        return doer_of_stuff
    return fngrabber

def distributeEvent(room, nodis, event):
    """Send an event to every object in the room unless they are on the 'nodis'
    list.
    """
    logging.debug('Distributing event %s' % event)
    for obj in room.contents:
        if obj not in nodis:
            obj.receiveEvent(event)

def adjs_num_parse((adjs, number)):
    adjs = frozenset(x.lower() for x in adjs)
    number = int(number) if number else 0
    return adjs, number

def get_from_rooms(blob, rooms, info):
    """Given the result of parsing an object_pattern (see actiondefs/core.py),
    this function can extract the object from a list of rooms, or raise an
    UnfoundError.
    """
    #circular import breaking.
    from grailmud.rooms import UnfoundError

    #XXX: some way of preserving state, so we can look at objects in more
    #detail but go on through them if the found one is not acceptable.
    if len(blob) == 2:
        adjs, num = adjs_num_parse(blob)
        for room in rooms:
            try:
                return room.matchContent(adjs, num)
            except UnfoundError:
                pass
        raise UnfoundError()
    elif len(blob) == 1:
        try:
            lowerkey = blob[0].lower()
            obj = info.instigator.targetting_shorts[lowerkey]
        except KeyError:
            raise UnfoundError
        for room in rooms:
            if obj in room:
                return obj
        raise UnfoundError()
    raise RuntimeError("Shouldn't get here.")

class smartdict(dict):
    """A dictionary that provides a mechanism for embedding expressions in
    format strings. Example:

    >>> "%(foo.upper())s" % smartdict(foo = "foo")
    'FOO'
    """
    def __getitem__(self, item):
        #convert to dict to prevent infinite recursion
        return eval(item, globals(), dict(self))

class InstanceTrackingMetaclass(type):
    '''A metaclass that removes some of the boilerplate needed for the
    InstanceTracker class.
    '''

    def __init__(cls, name, bases, dictionary):
        cls._instances = OSet()
        super(InstanceTrackingMetaclass,
              cls).__init__(name, bases, dictionary)

    def prefab_instances(cls, instances):
        """Insert a prefabricated list of instances into our instances list.
        """
        #upon consideration, this must be a no-op, because all the instances
        #will already be in the instances list thanks to the unpickling.
        #XXX: to be removed?
        pass

    def __call__(cls, *args, **kwargs):
        obj = super(InstanceTrackingMetaclass, cls).__call__(*args, **kwargs)
        InstanceTracker._creating_instances = True
        return obj

class TrueDict(dict):

    def __nonzero__(self):
        #hack to make sure __setstate__ is always called.
        return True

class InstanceTracker(object):
    '''A type that keeps track of its instances.'''

    __metaclass__ = InstanceTrackingMetaclass

    _creating_instances = False

    @classmethod
    def __new__(cls, *args, **kwargs):
        obj = object.__new__(cls)
        obj.add_to_instances()
        return obj

    def add_to_instances(self):
        """Register the object with its base types' instance trackers, and
        assign it the appropriate number.
        """
        classes = list(self.get_suitable_classes())
        for cls in classes:
            cls._instances.append(self)

    def remove_from_instances(self):
        """Remove the object from the instance trackers it has been registered
        to.
        """
        for cls in self.get_suitable_classes():
            if self in cls._instances:
                cls._instances.remove(self)

    def get_suitable_classes(self):
        """Return a generator that yields classes which keep track of
        instances.
        """
        for cls in type(self).__mro__:
            if '_instances' in cls.__dict__:
                yield cls

    def __setstate__(self, state):
        if InstanceTracker._creating_instances:
            self.remove_from_instances()
            raise RuntimeError("Don't unpickle stuff after the class has begun"
                               " normal construction.")
        self.__dict__.update(state)

    def __getstate__(self):
        return TrueDict(self.__dict__)

    #note that these will not survive pickling and comparisons against their
    #old values. However, there is a mechanism above to make sure that all
    #loading of pickles is done before new instance creation.
    def __hash__(self):
        return id(self)

    def __eq__(self, other):
        return self is other

class InstanceVariableFactoryMetaclass(type):

    def __init__(cls, name, bases, dictionary):
        cls._instance_variable_factories = {}
        super(InstanceVariableFactoryMetaclass,
              cls).__init__(name, bases, dictionary)

class InstanceVariableFactoryObject(object):

    __metaclass__ = InstanceVariableFactoryMetaclass
    
    def __getattribute__(self, attr):
        #please note, this method took a little while to get right, so don't
        #just change it willy-nilly. if something is here, it is here for a
        #reason, and not a hysterical one.
        if attr not in ('__dict__', '__class__'):
            if attr not in self.__dict__:
                for cls in type(self).__mro__:
                    if attr in getattr(cls, '_instance_variable_factories',
                                       {}):
                        res = cls._instance_variable_factories[attr](self)
                        setattr(self, attr, res)
                        return res

                if not any((attr in cls.__dict__) 
                            for cls in type(self).__mro__):
                    raise AttributeError()
            
        return object.__getattribute__(self, attr)

class BothAtOnceMetaclass(InstanceTrackingMetaclass,
                          InstanceVariableFactoryMetaclass):
    pass

class BothAtOnce(InstanceVariableFactoryObject, InstanceTracker):

    __metaclass__ = BothAtOnceMetaclass

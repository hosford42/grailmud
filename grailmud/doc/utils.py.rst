======================================
The ``utils.py`` module
======================================

``utils.py`` is a rather motley crew of functions and classes and bits and 
bobs. There are a few very useful looking bits of code in there that could be
extracted into a separate project or put into the Cookbook, and there are some
parts that are truly nothing but highly specialised utility functions for the
running of a MUD.

The ``smartdict``
-----------------

A ``smartdict`` functions very, very similarly to an actual ``dict``. It can
list its ``keys()``. It can list its ``values()``. It can even list both at
once. But the one point where it's different from a normal ``dict`` is an 
important one: instead of doing a simple hash-and-look-up for ``__getitem__``,
it actually evaluates the expression it's been handed, using itself as the
namespace.

For simple, name-permissible strings (for example, ``'foo'`` or ``'spam'``),
this functions exactly the same as it does normally (modulo the error raised
if the name isn't found, though this may be fixed at some point in the distant
future). But for more complicated and exotic strings, things diverge a little.

The main place that a ``smartdict`` becomes handy is in templating using normal
string interpolation - expressions such as::
    
    "%('foo'.upper())s" % smartdict()

become possible (the above example results in ``"FOO"``). As with all uses of
evaluation, this must be used with the utmost care and attention: it must be
ensured that there are no stray ``%`` characters in the string if it is 
untrusted (though ``s.replace('%', '%%')`` fixes that).

``InstanceTrackingMetaclass`` and ``InstanceTracker``
-----------------------------------------------------

These twinned classes do what sounds like a fairly simple job: they keep a
list (or, ``OrderedSet`` to be precise) of all the instances of a class that
inherits from ``InstanceTracker``. This list is stored in a class attribute
named ``_instances``; every superclass's ``_instances`` is a superset of its
subclasses' ``_instances``. That is, if there is a class ``Foo`` which inherits
from ``InstanceTracker``, all the ``Foo`` instances will appear in both 
``Foo._instances`` and ``InstanceTracker._instances``.

``InstanceTracker`` has sprouted a method of its own, or two. Apart from the
pickling and unpickling methods, it has ``add_to_instances``, which adds it to
all appropriate ``_instances``, ``remove_from_instances``, the inverse, and
``get_suitable_classes``, which is a generator that yields all the classes it
inherits from that have ``_instances`` attributes.

``InstanceTrackingMetaclass`` is a friendly and co-operative metaclass. It 
doesn't bully other metaclasses into submission (usually), but instead works
quite nicely with them.

The ``TrueDict``
----------------

Another ``dict`` derivative! This one has a much simpler modification - 
``bool(TrueDict(dictionary))`` will always return ``True``, no matter what the
value of ``dictionary`` is. This is used in the pickling mechanism of
``InstanceTracker`` (specifically, it is returned by ``__getstate__`` to ensure
``__setstate__`` is always called).

``defaultinstancevariable``
---------------------------

This prettymuch does what it says on the tin. The way a default instance 
variable works is that the object's class grows a descriptor which peeks into
the object's ``__dict__``. If it finds a value under its key, it returns that.
If not, it calls a specified function, sets the key in the ``__dict__`` to 
that, and returns the computed value.

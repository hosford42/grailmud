=============================
The delegate API
=============================

Delegates are objects which ``MUDObjects`` in the gameworld *delegate* their 
control to. This translates to the ``MUDObjects`` passing along the events 
which they are given to their delegates. ``MUDObjects``-to-delegates are a 
one-to-many relationship: each delegate (should) be tied to one MUDobject, but
a MUDObject can have many delegates attached.

The delegate API itself
=======================

``delegatee_event``
-----------------

This function takes an event as its sole parameter. (By and large, this will
mean inheriting from ``BaseEvent``, for ease of multimethod-ing). This will be
called when a MUDObject has been given an event and it needs to pass it on to
its delegates: this is that pass. There is no defined return value.

``event_flush``
-----------------

This function takes no parameters. It signifies that the current 'batch' of 
events are done; presently, automatically at the end of every tick.

Bits of the API that apply to ``MUDObjects``
=============================================

``addDelegate``
-----------------

This function is called with a single parameter, the delegate to attach to the
instance. This will raise an error if the delegate is already delegating.

``removeDelegate``
-------------------

The inverse of the above method. This removes the given delegate from the 
instance. This raises an error if the delegate is not delegating.

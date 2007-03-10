====================================
The architecture of ``grailmud``
====================================

The million-mile-high overview of ``grailmud``'s architecture is that there are 
objects in the MUD, controlled by (paradoxically) 'delegates', which perform 
various and disparate 'actions' to each other, and pass 'events' around to 
notify each other about these actions. Actions more-or-less correspond to 
functions, and events are actually implemented like this (see ``events.py``).

Objects receive these events and inform their delegates of this, and the 
delegates take the appropriate action - for NPCs, this may be attacking, or for
players, the event may be turned into text and sent down the tubes of Twisted. 

.. image:: informationflow.png

Thus we achieve a separation between business and display logic: actions do
their thing, and send the object an event without making any display decisions.
If the delegate that gets this event is a ``ConnectionHandler`` 
(``delegates.py``), then ``event.collapseToText`` will be called, textualising 
the event.


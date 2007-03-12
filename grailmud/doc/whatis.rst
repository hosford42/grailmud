==============================================
What is ``grailmud`` and why should I care?
==============================================

grailmud is a MUD server written entirely in Python (though optimising 
bottlenecks in C, and a more restricted language for builders and untrusted 
coders to work in are options which will be considered in the future) with a 
loosely coupled design between the game logic and the display logic for 
players, as well as a more loose than is traditional coupling between object 
logic and object state. grailmud also leverages Twisted, pyparsing and durus, 
so a bare minimum of low-level (networking|parsing|serialisation) code has to
be written.

These points make grailmud different from other (aspiring-to-be) 
production-ready MUD servers in this area (ie, MUDs written in Python). 
PythonMOO, POO, et al, have used a custom scripting language for programming 
game logic in, wheras grailmud uses Python for this task. Buyasta, wordplay, 
et al, have a tighter coupling between display and game logic. nakedmud 
reimplements a -lot- of stuff in C (ick!) which is already done in some
library, or which can be done painlessly in Python. There are many, many 
hackish little MUD servers written (I wrote 2 or 3 of them before I got the 
design more-or-less Right), but none of these are really suitable to build a 
whole game in.

One result of the decoupling of display and game logic is that the difference 
between player avatars and NPCs becomes the 'controller' (the object that 
receives the object's events and acts upon them) for players is linked to a 
socket (via the bowels of Twisted) and a few extra instance variables and 
methods on the player (eg, the player's password hash, and the method to take 
a line of input and dispatch it to the appropriate command). In more tightly 
coupled implementations, players and NPCs are different beasts entirely, 
possibly resulting in ridiculous duplication like different 'take away *X*
hitpoints' routines for each type, which should reside in a common base class.

Decoupling object logic and object state results in promoting 'controllers' 
(or as they ended up being called in the codebase, *delegates*, in the Self 
tradition) to first-class objects which can be added or removed from objects
at will. So if you want a staff to suddenly start acting like a goblin chief,
it becomes as simple as this::

    staff.addDelegate(GoblinChiefLogic())

rather than having to delve into the ``StaffObject``'s code and add the goblin
logic in there.


===============================
The ``emotefile.txt`` format
===============================

``actiondefs\emotefile.txt`` is used to define simple emotes.

Every single emote definition leads with the line ``emotedef:``, which is
followed by a space-delimited list of names. For each emote definition, there
can be up to three persons, which may or may not be required: ``first:``, seen
by the actor, ``second:``, seen by the target, and ``third:``, seen by everyone
else. They are followed by an emote line, possibly using pronoun punctuation.

Non-transitive emotes
---------------------

Non-transitive emotes have no target. They may be *solipsistic*, which means
that they are only seen in the first person, or not, which means that they
are visible in both the first and third person.

All non-transitive definitions are led by the line ``untargetted``.

Transitive emotes
-----------------

Transitive emotes have targets. They are always preceded by a non-transitive
definition, to use if the user didn't enter a valid target. They are always
visible in all three persons.

Pronoun punctuation key
-----------------------

``~`` (tilde)
    The actor performing the emote's short description.
``@`` (at-sign)
    The target of the emote's short description.

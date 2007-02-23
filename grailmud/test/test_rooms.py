from grailmud.rooms import Room, AnonyRoom, UnfoundError
from grailmud.objects import MUDObject, TargettableObject

def test_adding():
    r = Room('A blank room', 'Nothing to see here, move along.')
    obj = MUDObject(None)
    r.add(obj)
    assert obj in r.contents

def test_contains():
    r = Room('A blank room', 'Nothing to see here, move along.')
    obj = MUDObject(None)
    r.contents.add(obj)
    assert obj in r

def test_matchContent_with_number():
    r = AnonyRoom()
    for n in range(10):
        o = TargettableObject('a blob', set(['blob', 'grey']), r)
        r.add(o)
        if n == 5:
            seeking = o
        if n == 0:
            first = o

    assert r.matchContent(set(['grey', 'blob']), 5) is seeking
    assert r.matchContent(set(['grey']), 0) is first
#XXX: more should be here.

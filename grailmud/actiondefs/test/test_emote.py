from grailmud.actiondefs.emote import get_dict_definitions

simplein = '''
emotedef: lookup
untargetted
first: You look up.
'''

def test_parsing_solipsistic_emotes():
    res = list(get_dict_definitions(simplein))
    print res
    assert res == [{'names': ['lookup'],
                    'untargetted': {'first': 'You look up.'}}]

multiname = '''
emotedef: lookup, lookup2
untargetted
first: You look up.
'''

def test_parsing_multi_names():
    res = list(get_dict_definitions(multiname))
    print res
    assert res[0]['names'] == ['lookup', 'lookup2']

untargettedin = '''
emotedef: lookup
untargetted
first: You look up.
third: ~ looks up.
'''

def test_parsing_untargetted_emote():
    res = list(get_dict_definitions(untargettedin))
    print res
    assert res[0]['untargetted']['third'] == '~ looks up.'

targettedin = '''
emotedef: lookup
untargetted
first: You look up.
third: ~ looks up.
targetted
first: You look up at @.
second: ~ looks up at you.
third: ~ looks up at @.
'''

def test_parsing_targetted():
    res = list(get_dict_definitions(targettedin))
    print res
    assert res == [{'names': ['lookup'],
                    'untargetted': {'first': 'You look up.',
                                    'third': '~ looks up.'},
                    'targetted': {'first': 'You look up at @.',
                                  'second': '~ looks up at you.',
                                  'third': '~ looks up at @.'}}]

multiemotes = '''
emotedef: foobar
untargetted
first: foobar

emotedef: barbaz
untargetted
first: barbaz
'''

def test_multiple_emotes():
    res = list(get_dict_definitions(multiemotes))
    print res
    assert res == [{'names': ['foobar'],
                    'untargetted': {'first': 'foobar'}},
                   {'names': ['barbaz'],
                    'untargetted': {'first': 'barbaz'}}]

#XXX: testing for the rest of emote.py

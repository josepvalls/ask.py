#!/usr/bin/env python
# -*- coding: UTF-8 -*-

#
# This script generates permutations of a given string.
# Author: "Josep Valls-Vargas" <josep@valls.name>
# License: MIT
#

class UtteranceGenerator(object):
    @classmethod
    def generate(cls, grammar, dictionary={}, trim_whitespace=True, verbose=False):
        class ListOptions(list):
            def __repr__(self):
                return 'OP' + list.__repr__(self)

        class ListSequence(list):
            def __repr__(self):
                return 'SEQ<' + '-'.join([str(i) for i in self]) + '>'

        def consume(lst, until_token=None):
            ret = ''
            while lst:
                i = lst.pop(0)
                if i == until_token:
                    break
                else:
                    ret += i
            return ret

        def parse(lst, dictionary):
            options = ListOptions()
            current = ListSequence([''])
            # '(hello (this is|this is not) a test (yet|good))',
            while lst:
                i = lst.pop(0)
                if i == '(':
                    current.append(parse(lst, dictionary))
                    current.append('')
                elif i == ')':
                    options.append(current)
                    return options
                elif i == '|':
                    options.append(current)
                    current = ListSequence([''])
                elif i == '{':
                    options_ = ListOptions()
                    dictionary_name = consume(lst, '}')
                    if dictionary_name in dictionary:
                        for j in dictionary.get(dictionary_name, []):
                            options_.append(ListSequence([j]))
                    else:
                        options_.append(ListSequence(['{%s}' % dictionary_name]))
                    current.append(options_)
                    current.append('')
                elif i == '}':
                    pass  # this will be consumed and not in the string
                else:
                    current[-1] += i
            options.append(current)
            return options

        def check_whitespace(trim_whitespace, prev, next):
            if trim_whitespace and prev and next and prev.endswith(' ') and next[0] in ' .,;:?!':
                return prev.rstrip() + next
            else:
                return prev + next

        def generate(seq, current=None, lst=[]):
            ret = []
            current_ = current or ['']

            if not seq:
                return current_
            else:
                for current_i in current_:
                    car = seq[0]
                    cdr = seq[1:]
                    if isinstance(car, str):
                        ret.append(check_whitespace(trim_whitespace, current_i, car))
                    elif isinstance(car, ListOptions):
                        for option in car:
                            ret_ = generate(option)
                            for i in ret_:
                                ret.append(check_whitespace(trim_whitespace, current_i,i))
                return generate(cdr, ret)

        results = []

        for line in grammar:
            p = ListSequence([parse(list(line), dictionary)])
            if verbose:
                print p
            for i in generate(p):
                if verbose:
                    print ' ', i
                results.append(i)
        return results

def test_generator():
    d = {}
    g = [
        # the following are for my Audio Battleship skill
        'ShootIntent (|do|do a) (|shoot|shot|attack|fire|strike|airstrike|target) (|at|to) {Column} {Row}',
        'ShootIntent (|launch|do) (|a) torpedo (|at|to) {Column} {Row}',
        'NewIntent (start|start a|start a new|a new|new) (game|board) (| (|of) (|Audio) (battleship|naval battle))',
        # the following are for my Audio Hangman skill
        'NewIntent (start|start a|start a new|a new|new) game (| (|of) (|Audio) hangman',
        'GuessIntent (|get|give|give me|guess|check) {Letter}',
        # the following are for my Dark Cave skill
        'NewIntent (start|start a|start a new|a new|new) game (| (|of) dark cave',
        'ShootIntent (shoot|fire|launch) (|one|a|the) (|arrow)',
        'TurnIntent turn {Direction}',
        'WalkIntent (walk|move|go|step|) (forward|ahead|straight|)',
        'PickupIntent (grab|pickup|pick up|pick|take|catch|seize|snatch) (|gold|pile|pile of gold|gold pile|arrow)'
        # the following are for my Easy Hangman skill
        'NewIntent (start|start a|start a new|a new|new) game (| (|of) (|easy) hangman',
        'GuessIntent (|get|guess|check) (for the|) (letter|) ({Letter}|((a|b|c|d|e|f|g|h|i|j|k|l|m|n|o|p|q|r|s|t|u|v|w|x|y|z)(.|)) (as in|like) {Letter})',
        'ClueIntent (give|say|tell) (|me) (|a) (clue|hint)'
    ]
    results = UtteranceGenerator().generate(g, d, verbose=False)
    for i in results:
        print i

if __name__=="__main__":
    test_generator()


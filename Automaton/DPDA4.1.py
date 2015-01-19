#!/usr/bin/env python3.4

"""Deterministic PushDown Automaton，DPDA"""

# "Understanding Computation: Impossible Code and the Meaning of Programs"
# Chapter 4.1 's Code. Use Python3.
# Authors: Chai Fei

class Stack(object):
    """ The realization of the stack
    """
    def __init__(self, contents):
        self.contents = contents

    def push(self, character):
        return Stack([character] + self.contents)

    @property
    def pop(self):
        return Stack(self.contents[1:])

    @property
    def top(self):
        return self.contents[0]

    def __str__(self):
        top = self.contents[0]
        underside = ''.join(self.contents[1:])
        return '#<Stack ({top}){underside}>'.format(**locals())

    __repr__ = __str__


class PDAConfiguration(object):
    """ Used to store the PDA configuration (a state and a stack)
    """
    def __init__(self, state, stack):
        self.state = state
        self.stack = stack

    def __str__(self):
        state = self.state
        stack = repr(self.stack)
        return '#<struct PDAConfiguration state={state}, stack={stack}>'.format(**locals())

    __repr__ = __str__


class PDARule(object):
    """ Used to express a rule, in a rule book of PDA
    """
    def __init__(self, state, character, next_state, pop_character, push_characters):
        self.state = state
        self.character = character
        self.next_state = next_state
        self.pop_character = pop_character
        self.push_characters = push_characters

    def applies_to(self, configuration, character):
        return self.state == configuration.state and \
                self.pop_character == configuration.stack.top and \
                self.character == character

    def follow(self, configuration):
        return PDAConfiguration(self.next_state, self.next_stack(configuration))

    def next_stack(self, configuration):
        popped_stack = configuration.stack.pop
        for item in self.push_characters[::-1]:
            popped_stack = popped_stack.push(item)
        return popped_stack

    def __str__(self):
        s = repr(self.state)
        char = repr(self.character)
        nexts = repr(self.next_state)
        pop_char = repr(self.pop_character)
        push_chars = repr(self.push_characters)
        
        return '#<struct PDARule\n\
        state={s},\n\
        character={char},\n\
        next_state={nexts},\n\
        pop_character={pop_char},\n\
        push_characters={push_chars}'.format(**locals())

    __repr__ = __str__


class DPDARulebook(object):
    def __init__(self, rules):
        self.rules = rules

    def next_configuration(self, configuration, character):
        return self.rule_for(configuration, character).follow(configuration)

    def rule_for(self, configuration, character):
        for rule in self.rules:
            if rule.applies_to(configuration, character):
                return rule


class DPDA(object):
    def __init__(self, current_configuration, accept_states, rulebook):
        self.current_configuration = current_configuration
        self.accept_states = accept_states
        self.rulebook = rulebook

    @property
    def accepting(self):
        if self.current_configuration.state in self.accept_states:
            return True
        else:
            return False

    def read_character(self, character):
        self.current_configuration = self.rulebook.next_configuration(self.current_configuration, character)

    def read_string(self, string):
        for char in string:
            self.read_character(char)


## UnitTest
import unittest

class TestDPDA(unittest.TestCase):
    """ Tests of the books's code
    """
        
    def test_Stack(self):
        stack = Stack(['a','b','c','d','e'])
        self.assertEqual(str(stack), '#<Stack (a)bcde>')
        self.assertEqual(stack.pop.pop.top, 'c')
        self.assertEqual(stack.push('x').push('y').top, 'y')
        self.assertEqual(stack.push('x').push('y').pop.top, 'x')

    def test_PDARule(self):
        rule = PDARule(1, '(', 2, '$', ['b', '$'])
        configuration = PDAConfiguration(1, Stack(['$']))
        print(rule, end = '\n\n')
        self.assertEqual(str(configuration), '#<struct PDAConfiguration state=1, stack=#<Stack ($)>>')
        self.assertEqual(rule.applies_to(configuration, '('), True)

        self.assertEqual(str(rule.follow(configuration)), '#<struct PDAConfiguration state=2, stack=#<Stack (b)$>>')

    def test_DPDARulebook(self):
        rulebook = DPDARulebook([
            PDARule(1, '(', 2, '$', ['b', '$']),
            PDARule(2, '(', 2, 'b', ['b', 'b']),
            PDARule(2, ')', 2, 'b', []),
            PDARule(2, None, 1, '$', ['$'])
        ])
        configuration = PDAConfiguration(1, Stack(['$']))
        configuration = rulebook.next_configuration(configuration, '(')
        self.assertEqual(str(configuration), '#<struct PDAConfiguration state=2, stack=#<Stack (b)$>>')
        configuration = rulebook.next_configuration(configuration, '(')
        self.assertEqual(str(configuration), '#<struct PDAConfiguration state=2, stack=#<Stack (b)b$>>')
        configuration = rulebook.next_configuration(configuration, ')')
        self.assertEqual(str(configuration), '#<struct PDAConfiguration state=2, stack=#<Stack (b)$>>')

    def test_DPDA(self):
        rulebook = DPDARulebook([
            PDARule(1, '(', 2, '$', ['b', '$']),
            PDARule(2, '(', 2, 'b', ['b', 'b']),
            PDARule(2, ')', 2, 'b', []),
            PDARule(2, None, 1, '$', ['$'])
        ])
        dpda = DPDA(PDAConfiguration(1, Stack(['$'])), [1], rulebook)
        self.assertEqual(dpda.accepting, True)
        dpda.read_string('(()')
        self.assertEqual(dpda.accepting, False)
        self.assertEqual(str(dpda.current_configuration), '#<struct PDAConfiguration state=2, stack=#<Stack (b)$>>')
        

if __name__ == '__main__':
    unittest.main()

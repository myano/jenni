#!/usr/bin/env python
'''
ask.py - jenni's Ask Module, randomly select from a given list or provide a yes/no response

Copyright 2014-2016, Josh Begleiter (jbegleiter.com)
Copyright 2011-2016, Michael Yanovich (yanovich.net)
Licensed under the Eiffel Forum License 2.

More info:
 * jenni: https://github.com/myano/jenni/
 * Phenny: http://inamidst.com/phenny/
'''

from random import choice, seed
import time

seed()

def ask(jenni, input):
    '''.ask <item1> or <item2> or <item3> - Randomly picks from a set of items seperated by ' or '.'''

    choices = input.group(2)

    if choices is None:
        jenni.reply('There is no spoon! Please try a valid question.')
        return

    lower_case_choices = choices.lower()
    if lower_case_choices == 'what is the answer to life, the universe, and everything?':
        ## cf. https://is.gd/2KYchV
        jenni.reply('42')
    else:
        list_choices = []

        # If we think the separator is parallel pipes instead of 'or'
        if ' || ' in lower_case_choices:
            list_choices = lower_case_choices.split(' || ')
        else:
            list_choices = lower_case_choices.split(' or ')

        if len(list_choices) == 1:
            ## if multiple things aren't listed
            ## default to yes/no
            jenni.reply(choice(['yes', 'no']))
        else:
            ## randomly pick an item if multiple things
            ## are listed
            jenni.reply((choice(list_choices)).encode('utf-8'))
ask.commands = ['ask']
ask.priority = 'low'
ask.example = '.ask today || tomorrow || next week'

if __name__ == '__main__':
    print __doc__.strip()


#!/usr/bin/env python
'''
smiley.py - Smiley Module
Copyright 2014 Sujeet Akula (sujeet@freeboson.org)
Licensed under the Eiffel Forum License 2.

More info:
 * jenni-misc: https://github.com/freeboson/jenni-misc/
 * jenni: https://github.com/myano/jenni/
 * Phenny: http://inamidst.com/phenny/
'''

import io, random, os

def smiley(jenni, input):
    '''.smiley -- print a random smiley'''

    with io.open(os.getcwd() + 'modules/smileys.txt', 'r', encoding='utf-16-le') as f:
        smileys = f.read().splitlines()
        jenni.say(random.choice(smileys))

smiley.commands = ['smiley']
smiley.priority = 'low'

if __name__ == '__main__':
    print __doc__.strip()


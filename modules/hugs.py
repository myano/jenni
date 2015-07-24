#!/usr/bin/env python
"""
hugs.py - jenni Hugs Module
Copyright 2015, Michael Yanovich (yanovich.net)
Licensed under the Eiffel Forum License 2.

More info:
 * jenni: https://github.com/myano/jenni/
 * Phenny: http://inamidst.com/phenny/
"""


def hugs(jenni, input):
    '''.hugs <nick> -- have jenni hug somebody'''
    txt = input.group(2)
    if not txt:
        msg = '\x01ACTION hugs %s\x01' % (input.nick)
        return jenni.msg(input.sender, msg, x=True)
    parts = txt.split()
    to = parts[0]
    if to == jenni.config.nick:
        to = 'themself'

    msg = '\x01ACTION hugs %s\x01' % (to)
    jenni.msg(input.sender, msg, x=True)
hugs.commands = ['hug', 'hugs']

if __name__ == '__main__':
    print __doc__.strip()

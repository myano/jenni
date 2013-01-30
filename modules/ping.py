#!/usr/bin/env python
"""
ping.py - jenni Ping Module
Copyright 2009-2013, Michael Yanovich (yanovich.net)
Copyright 2008-2013, Sean B. Palmer (inamidst.com)

More info:
 * jenni: https://github.com/myano/jenni/
 * Phenny: http://inamidst.com/phenny/
"""

import random

def interjection(jenni, input):
    jenni.say(input.nick + '!')
interjection.rule = r'($nickname!)'
interjection.priority = 'high'
interjection.thread = False
interjection.rate = 30

if __name__ == '__main__':
    print __doc__.strip()

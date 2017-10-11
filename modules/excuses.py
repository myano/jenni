#!/usr/bin/env python
"""
excuses.py - jenni Excuse Module
Copyright 2009-2013, Michael Yanovich (yanovich.net)
Licensed under the Eiffel Forum License 2.

More info:
 * jenni: https://github.com/myano/jenni/
 * Phenny: http://inamidst.com/phenny/
"""

import re
from modules import proxy
import web


def excuse(jenni, input):
    a = re.compile('<a [\s\S]+>(.*)</a>')

    try:
        page = proxy.get('http://programmingexcuses.com/')
    except:
        return jenni.say("I'm all out of excuses!")

    results = a.findall(page)

    if results:
        result = results[0]
        result = result.strip()
        if result[-1] not in ['.', '?', '!']:
            result += '.'
        jenni.say(result)
    else:
        jenni.say("I'm too lazy to find an excuse.")
excuse.commands = ['excuse', 'excuses']


if __name__ == '__main__':
    print __doc__.strip()

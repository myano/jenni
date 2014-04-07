#!/usr/bin/env python
"""
man.py - jenni man page linker
Copyright 2009-2013, Michael Yanovich (yanovich.net)
Copyright 2008-2013, Sean B. Palmer (inamidst.com)
Licensed under the Eiffel Forum License 2.

Developed by kaneda (https://jbegleiter.com / https://github.com/kaneda)

More info:
 * jenni: https://github.com/myano/jenni/
 * Phenny: http://inamidst.com/phenny/
"""

import re
import traceback
import urllib
import urlparse

try:
    from BeautifulSoup import BeautifulSoup as Soup
except ImportError:
    raise ImportError("Could not find BeautifulSoup library,"
                      "please install to use the man module")

man_uri = "http://man.he.net/?topic=%s&section=all"
not_found = "No matches for \"%s\""

def man(jenni, input):
    global man_uri
    global not_found

    term = input.groups()[1]
    if not term:
        return jenni.say('Perhaps you meant ".man ls"?')

    if len(term.split(' ')) > 1:
        return jenni.say('I was expecting only one search term')

    t = urllib.quote_plus(term)
    n = not_found % term
    # URL encode the term given
    if '%' in term:
        t = urllib.quote_plus(term.replace('%', ''))
        n = not found % term.replace('%','')

    content = urllib.urlopen(man_uri % t).read()
    soup = Soup(content)
    h2s = soup.findAll('h2')

    for h in h2s:
        if n in h:
            return jenni.say("Couldn't find the man page {0} on man.he.net".format(term))

    jenni.say(man_uri % t)
    jenni.say("I am sending you the content of this page in a private message")
    for c in soup.pre.contents[0].split('\n'):
        jenni.msg(input.nick, c, False, False, 1)

man.commands = ['man', 'manual']
man.priority = 'high'
man.rate = 10

if __name__ == '__main__':
    print __doc__.strip()

#!/usr/bin/env python
"""
seen.py - jenni Seen Module
Copyright 2009-2013, Michael Yanovich (yanovich.net)
Copyright 2008-2013, Sean B. Palmer (inamidst.com)
Licensed under the Eiffel Forum License 2.

More info:
 * jenni: https://github.com/myano/jenni/
 * Phenny: http://inamidst.com/phenny/
"""

import time

## TODO: Make it save .db to disk

def f_seen(jenni, input):
    """.seen <nick> - Reports when <nick> was last seen."""

    if not input.group(2):
        return jenni.say('Please provide a nick.')
    nick = input.group(2).lower()

    if not hasattr(jenni, 'seen'):
        return jenni.reply('?')

    if jenni.seen.has_key(nick):
        channel, t = jenni.seen[nick]
        t = time.strftime('%Y-%m-%d %H:%M:%S UTC', time.gmtime(t))
        msg = 'I last saw %s at %s in some channel.' % (nick, t)
        jenni.say(msg)
    else:
        jenni.say("Sorry, I haven't seen %s around." % nick)
f_seen.rule = r'(?i)^\.(seen)\s+(\w+)'
f_seen.rate = 15

def f_note(jenni, input):
    try:
        if not hasattr(jenni, 'seen'):
            jenni.seen = dict()
        if input.sender.startswith('#'):
            jenni.seen[input.nick.lower()] = (input.sender, time.time())
    except Exception, e: print e
f_note.rule = r'(.*)'
f_note.priority = 'low'

if __name__ == '__main__':
    print __doc__.strip()

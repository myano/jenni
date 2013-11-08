#!/usr/bin/env python
'''
xkcd.py - XKCD Module
Copyright 2010-2013 Michael Yanovich (yanovich.net), and Morgan Goose
Licensed under the Eiffel Forum License 2.

More info:
 * jenni: https://github.com/myano/jenni/
 * Phenny: http://inamidst.com/phenny/
'''

import json
import random
import web


random.seed()


def xkcd(jenni, input):
    '''.xkcd - Generates a url for a random XKCD clip.'''

    try:
        page = web.get('https://xkcd.com/info.0.json')
    except:
        return jenni.say('Failed to access xkcd.com')

    try:
        body = json.loads(page)
    except:
        return jenni.say('Failed to make use of data loaded by xkcd.com')

    max_int = body['num']
    website = 'https://xkcd.com/%d/' % random.randint(0, max_int)
    jenni.say(website)
xkcd.commands = ['xkcd']
xkcd.priority = 'low'
xkcd.rate = 10

if __name__ == '__main__':
    print __doc__.strip()

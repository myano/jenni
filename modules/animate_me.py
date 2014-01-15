#!/usr/bin/env python
"""
image_me.py - jenni Animated GIF Fetcher Module
Copyright 2009-2013, Michael Yanovich (yanovich.net)
Copyright 2008-2013, Sean B. Palmer (inamidst.com)
Licensed under the Eiffel Forum License 2.

Developed by kaneda (https://josh.myhugesite.com / https://github.com/kaneda)

More info:
 * jenni: https://github.com/myano/jenni/
 * Phenny: http://inamidst.com/phenny/
"""

import random
import re
import traceback
import urllib
import urlparse

try:
    from BeautifulSoup import BeautifulSoup as Soup
except ImportError:
    raise ImportError("Could not find BeautifulSoup library,"
                      "please install to use the image_me module.")

giphy_uri = 'http://giphy.com/search/%s'
alpha_pattern = re.compile('[^ A-Za-z0-9_-]*')

giphy_image = 'http://media.giphy.com/media/%s/giphy.gif'


def animate_me(term):
    global giphy_uri

    t = alpha_pattern.sub('', term)
    # URL encode the term given
    if ' ' in term:
        t = term.replace(' ', '-')

    content = urllib.urlopen(giphy_uri % t).read()
    soup = Soup(content)
    data_ids = [a['data-id'] for a in soup.findAll('a', 'a-gif', href=True)]

    if data_ids:
        data_id = data_ids[random.randint(0, len(data_ids) - 1)]
        return giphy_image % data_id


def gif(jenni, input):
    origterm = input.groups()[1]
    if not origterm:
        return jenni.say('Perhaps you meant ".animate_me pugs"?')
    origterm = origterm.encode('utf-8')
    origterm = origterm.strip()

    error = None

    try:
        result = animate_me(origterm)
    except IOError:
        error = "An error occurred connecting to Giphy"
        traceback.print_exc()
    except Exception as e:
        error = "An unknown error occurred: " + str(e)
        traceback.print_exc()

    if error is not None:
        jenni.say(error)
    elif result is not None:
        jenni.say(result)
    else:
        jenni.say('Can\'t find anything in Giphy for "%s".' % origterm)

gif.commands = ['animate_me', 'nm8_me']
gif.priority = 'high'
gif.rate = 10

if __name__ == '__main__':
    print __doc__.strip()

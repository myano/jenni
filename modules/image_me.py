#!/usr/bin/env python
"""
image_me.py - jenni Image Fetcher Module
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
from modules import proxy

try:
    from BeautifulSoup import BeautifulSoup as Soup
except ImportError:
    raise ImportError("Could not find BeautifulSoup library,"
                      "please install to use the image_me module")

google_images_uri = 'https://www.google.com/search?safe=off'
google_images_uri += '&source=lnms&tbm=isch&q=%s'


def image_me(term):
    global google_images_uri

    t = urllib.quote_plus(term)
    # URL encode the term given
    if '%' in term:
        t = urllib.quote_plus(term.replace('%', ''))

    content = proxy.get(google_images_uri % t)

    soup = Soup(content)
    img_links = [a['href'] for a in soup.findAll('a', 'rg_l', href=True)]

    if img_links:
        full_link = img_links[random.randint(0, len(img_links) - 1)]
        parsed_link = urlparse.urlparse(full_link)
        query = urlparse.parse_qs(parsed_link.query)
        img_url = query['imgurl']
        if type(img_url) == list:
            img_url = img_url[0]
        return urllib.unquote_plus(img_url)


def img(jenni, input):
    origterm = input.groups()[1]
    if not origterm:
        return jenni.say('Perhaps you meant ".image_me pugs"?')
    origterm = origterm.encode('utf-8')
    origterm = origterm.strip()

    error = None

    try:
        result = image_me(origterm)
    except IOError:
        error = "An error occurred connecting to Google Images"
        traceback.print_exc()
    except Exception as e:
        error = "An unknown error occurred: " + str(e)
        traceback.print_exc()

    if error is not None:
        jenni.say(error)
    elif result is not None:
        jenni.say(result)
    else:
        jenni.say('Can\'t find anything in Google Images for "%s".' % origterm)

img.commands = ['img_me', 'image_me']
img.priority = 'high'
img.rate = 10

if __name__ == '__main__':
    print __doc__.strip()

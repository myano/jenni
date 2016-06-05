#!/usr/bin/env python
"""
image_me.py - jenni Image Fetcher Module
Copyright 2014-2016, Josh Begleiter (jbegleiter.com)
Copyright 2009-2013, Michael Yanovich (yanovich.net)
Copyright 2008-2013, Sean B. Palmer (inamidst.com)
Licensed under the Eiffel Forum License 2.

More info:
 * jenni: https://github.com/myano/jenni/
 * Phenny: http://inamidst.com/phenny/
"""

import json
import random
import re
import traceback
import urllib,urllib2
import urlparse
from modules import proxy

def image_me(jenni, term):
    google_images_uri = 'https://www.googleapis.com/customsearch/v1?start=1&searchType=image'

    search_uri = '{0}&q={1}&key={2}&cx={3}'.format(
        google_images_uri,
        urllib.quote_plus(term),
        jenni.config.google_dev_apikey,
        jenni.config.google_custom_search_key
    )

    try:
        content = urllib2.urlopen(search_uri).read()
    except Exception as e:
        jenni.say("Failed to contact Google Search, please try again later")
        print "Failed to contact Google Search in image_me: {0}".format(e)
        return

    try:
        img_json = json.loads(content)
    except Exception as e:
        jenni.say("An error occurred getting image results, check logs for more details")
        print "Failed to parse JSON for image_me: {0}\n{1}".format(e, content)
        return

    if "items" not in img_json:
        jenni.say("No results found")
        return

    img_links = [item["link"] for item in img_json["items"]]

    if img_links:
        full_link = img_links[random.randint(0, len(img_links) - 1)]
        return full_link


def img(jenni, input):
    origterm = input.groups()[1]
    if not origterm:
        return jenni.say('Perhaps you meant ".image_me pugs"?')
    origterm = origterm.encode('utf-8')
    origterm = origterm.strip()

    error = None

    try:
        result = image_me(jenni, origterm)
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

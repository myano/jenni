#!/usr/bin/env python
"""
mustache_me.py - jenni Mustachifier Module
Copyright 2009-2013, Michael Yanovich (yanovich.net)
Copyright 2008-2013, Sean B. Palmer (inamidst.com)
Licensed under the Eiffel Forum License 2.

Developed by kaneda (https://josh.myhugesite.com / https://github.com/kaneda)

More info:
 * jenni: https://github.com/myano/jenni/
 * Phenny: http://inamidst.com/phenny/
"""

try:
    from modules import image_me
except ImportError:
    raise ImportError("You must have the image_me module to use"
                      "the mustache_me module")

mustache_uri = 'http://mustachify.me/?src=%s'


def mustache_me(term):
    quoted_url = image_me.image_me(term)

    global mustache_uri

    if quoted_url:
        return (mustache_uri % quoted_url)


def mustache(jenni, input):
    origterm = input.groups()[1]
    if not origterm:
        return jenni.say('Perhaps you meant ".mustache_me pugs"?')
    origterm = origterm.encode('utf-8')
    origterm = origterm.strip()

    error = None

    try:
        result = mustache_me(origterm)
    except IOError:
        error = "An error occurred connecting to Google Images"
        error += "or the mustachifier"
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

mustache.commands = ['mustache_me']
mustache.priority = 'high'
mustache.rate = 10

if __name__ == '__main__':
    print __doc__.strip()

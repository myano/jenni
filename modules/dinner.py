#!/usr/bin/env python
'''
dinner.py - Dinner Module
Copyright 2013 Michael Yanovich (yanovich.net)
Copyright 2013 Unknown
Licensed under the Eiffel Forum License 2.

More info:
 * jenni: https://github.com/myano/jenni/
 * Phenny: http://inamidst.com/phenny/
'''

import re
import web


def fucking_dinner(jenni, input):
    '''.fd -- provide suggestions for dinner'''
    txt = input.group(2)
    url = 'http://www.whatthefuckshouldimakefordinner.com'
    if txt == '-v':
        url = 'http://whatthefuckshouldimakefordinner.com/veg.php'
    page = web.get(url)
    re_mark = re.compile('<dt><a href="(.*?)" target="_blank">(.*?)</a></dt>')
    results = re_mark.findall(page)
    if results:
        jenni.say("WHY DON'T YOU EAT SOME FUCKING: " + results[0][1] +
                  " HERE IS THE RECIPE: " + results[0][0])
    else:
        jenni.say("I DON'T FUCKING KNOW, EAT PIZZA.")
fucking_dinner.commands = ['fucking_dinner', 'fd', 'wtfsimfd']
fucking_dinner.priority = 'low'

if __name__ == '__main__':
    print __doc__.strip()

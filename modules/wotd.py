#!/usr/bin/env python
"""
wotd.py - jenni word of the day module
Copyright 2013 Michael Yanovich (yanovich.net)
Licensed under the Eiffel Forum License 2.

More info:
 * jenni: https://github.com/myano/jenni/
 * Phenny: http://inamidst.com/phenny/
"""

import re
import web

re_word = re.compile("<h3>\n(.*?)\n</h3>")
re_pronounce = re.compile('PRONUNCIATION:</div>\n<div style="margin-left: 20px;">\n(.*?)\n')
re_meaning = re.compile('MEANING:</div>\n<div style="margin-left: 20px;">\n(.*?)\n')
re_usage = re.compile('USAGE:</div>\n<div style="margin-left: 20px;">\n([\n\s\S]*?)\n</div>')


def wotd(jenni, input):
    """.wotd -- provies a word of the day"""
    page = web.get("http://wordsmith.org/words/today.html")
    word = re_word.findall(page)
    pronounce = re_pronounce.findall(page)
    meaning = re_meaning.findall(page)
    usage = re_usage.findall(page)
    template = "%s %s [%s]: %s -- Usage: %s"

    if word and pronounce and meaning and usage:
        wordtype = meaning[0].split(">")[1][:-3]
        usage = usage[0].replace("\n", " ")
        usage = usage.replace("<br>", "")
        output = template % (word[0], pronounce[0], wordtype,
                             meaning[0].split(": ")[1], usage)
    else:
        output = "No word for today is available."

    jenni.say(output)
wotd.commands = ['wotd']
wotd.priority = 'low'
wotd.rate = 20

if __name__ == '__main__':
    print __doc__.strip()

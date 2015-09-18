#!/usr/bin/env python
"""
pun.py - jenni Pun Module
Copyright 2009-2015, Michael Yanovich (yanovich.net)
Copyright 2008-2015, Sean B. Palmer (inamidst.com)
Copyright 2015, Jonathan Arnett (j3rn.com)

More info:
 * jenni: https://github.com/myano/jenni/
 * Phenny: http://inamidst.com/phenny/
"""

import re
from modules import proxy
import web

def puns(jenni, input):
    url = 'http://www.punoftheday.com/cgi-bin/randompun.pl'
    exp = re.compile(r'<div class="dropshadow1">\n<p>(.*?)</p>\n</div>')
    page = proxy.get(url)

    result = exp.search(page)
    if result:
        pun = result.groups()[0]
        jenni.say(pun)
    else:
        jenni.say("I'm afraid I'm not feeling punny today!")

puns.priority = 'low'
puns.commands = ['puns', 'pun']

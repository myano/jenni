#!/usr/bin/env python
"""
chat.py - jenni's Chat Module
Copyright 2013, Michael Yanovich (yanovich.net)
Licensed under the Eiffel Forum License 2.

More info:
 * jenni: https://github.com/myano/jenni/
 * Phenny: http://inamidst.com/phenny/
"""


import cleverbot
import json
import random
import re
import time
import web

mycb = cleverbot.Session()

nowords = ['reload', 'help', 'tell', 'ask']


def chat(jenni, input):
    txt = input.groups()
    if len(txt) > 0:
        text = txt[1]
        if txt[1].startswith('\x03') or txt[1].startswith('\x01'):
            ## block out /ctcp
            return
    else:
        print time.time(), 'Something went wrong with chat.py'
        return

    if not text:
        return
    channel = input.sender
    for x in nowords:
        if text.startswith(x):
            return
    msgi = text.strip()
    msgo = str()
    if channel.startswith('#') and txt[0]:
        ## in a channel and prepended with jenni's name
        pm = False
        msgo = mycb.Ask(msgi)
    elif not channel.startswith('#'):
        ## in a PM and not prepended with jenni's name
        pm = True
        if text.startswith('.'):
            return
        elif text.startswith(jenni.config.nick + ':'):
            spt = text.split(':')[1].strip()
            for x in nowords:
                if spt.startswith(x):
                    return
        msgo = mycb.Ask(msgi)
    else:
        ## anything else
        return
    if msgo:
        rand_num = random.randint(0, 10)
        time.sleep(3 + rand_num)
        response = re.sub('(?i)cleverbot', 'jenni', msgo)
        if pm:
            jenni.say(response)
            beginning = ':%s PRIVMSG %s :' % (jenni.config.nick, input.sender)
            if hasattr(jenni.config, 'logchan_pm'):
                jenni.msg(jenni.config.logchan_pm, beginning + response)
        else:
            jenni.reply(response)
chat.rule = r'(?i)($nickname[:,]?\s)?(.*)'

if __name__ == '__main__':
    print __doc__.strip()

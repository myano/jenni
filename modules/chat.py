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
from htmlentitydefs import name2codepoint
import json
from modules import unicode as uc
import random
import re
import time

mycb = cleverbot.Session()

nowords = ['reload', 'help', 'tell', 'ask']

r_entity = re.compile(r'&[A-Za-z0-9#]+;')
HTML_ENTITIES = { 'apos': "'" }

random.seed()


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
        try:
            msgo = mycb.Ask(msgi)
        except:
            return
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
        try:
            msgo = mycb.Ask(msgi)
        except:
            return
    else:
        return
    print 'msgo:', list(msgo)
    if msgo:
        rand_num = random.randint(0, 15)
        time.sleep(3 + rand_num)
        response = re.sub('(?i)cleverbot', 'jenni', msgo)
        response = r_entity.sub(e, response)
        if pm:
            jenni.say(response)
            beginning = ':%s PRIVMSG %s :' % (jenni.config.nick, input.sender)
            if hasattr(jenni.config, 'logchan_pm'):
                jenni.msg(jenni.config.logchan_pm, beginning + response)
        else:
            delim = random.choice((',', ':'))
            msg = '%s%s %s' % (input.nick, delim, response)
            jenni.say(msg)
chat.rule = r'(?i)($nickname[:,]?\s)?(.*)'


def e(m):
    entity = m.group()
    if entity.startswith('&#x'):
        cp = int(entity[3:-1], 16)
        meep = unichr(cp)
    elif entity.startswith('&#'):
        cp = int(entity[2:-1])
        meep = unichr(cp)
    else:
        entity_stripped = entity[1:-1]
        try:
            char = name2codepoint[entity_stripped]
            meep = unichr(char)
        except:
            if entity_stripped in HTML_ENTITIES:
                meep = HTML_ENTITIES[entity_stripped]
            else:
                meep = str()
    try:
        return uc.decode(meep)
    except:
        return uc.decode(uc.encode(meep))


if __name__ == '__main__':
    print __doc__.strip()

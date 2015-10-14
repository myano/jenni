#!/usr/bin/env python
"""
chat.py - jenni's Chat Module
Copyright 2013, Michael Yanovich (yanovich.net)
Licensed under the Eiffel Forum License 2.

More info:
 * jenni: https://github.com/myano/jenni/
 * Phenny: http://inamidst.com/phenny/
"""


from modules import cleverbot
from htmlentitydefs import name2codepoint
import json
from modules import unicode as uc
import random
import re
import time

mycb = cleverbot.Cleverbot()

nowords = ['reload', 'help', 'tell', 'ask', 'ping']

r_entity = re.compile(r'&[A-Za-z0-9#]+;')
HTML_ENTITIES = { 'apos': "'" }
noun = 'ZHVjaw=='

random.seed()


def chat(jenni, input):
    txt = str()
    if input.groups():
        txt = input.groups()
    else:
        txt = input.bytes

    text = None

    if len(txt) > 1:
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
            time.sleep(random.randint(5, 30))
            msgo = mycb.ask(msgi)
        except:
            return
    elif not channel.startswith('#'):
        ## in a PM and not prepended with jenni's name
        pm = True
        if text.startswith('.') or (hasattr(jenni.config, 'prefix') and text.startswith(jenni.config.prefix)):
            return
        elif text.startswith(jenni.config.nick + ':'):
            spt = text.split(':')[1].strip()
            for x in nowords:
                if spt.startswith(x):
                    return
        try:
            time.sleep(random.randint(3, 15))
            msgo = mycb.ask(msgi)
        except:
            return
    else:
        return

    if msgo:
        rand_num = random.randint(0, 5)
        time.sleep(1 + rand_num)

        response = re.sub('(?i)cleverbot', 'jenni', msgo)
        response = re.sub('(?i)\b\S+bot\b', noun.decode('base64'), response)
        response = re.sub('(?i)\bbot\b', noun.decode('base64'), response)
        response = re.sub('(?i)\bcomputer\b', noun.decode('base64'), response)
        response = r_entity.sub(e, response)

        if random.random() <= 0.5:
            response = response[0].lower() + response[1:]

        if random.random() <= 0.5:
            response = response[:-1]

        def chomp(txt):
            random_int_rm = random.randint(1, len(txt))
            return txt[:random_int_rm-1] + txt[random_int_rm:]

        if random.random() <= 0.25:
            l_response = len(response) // 20
            for x in range(1, l_response):
                response = chomp(response)

        if pm:
            jenni.say(response)
            beginning = ':%s PRIVMSG %s :' % (jenni.config.nick, input.sender)
            if hasattr(jenni.config, 'logchan_pm'):
                jenni.msg(jenni.config.logchan_pm, beginning + response)
        else:
            delim = random.choice((',', ':'))
            msg = '%s' % (response)

            if random.random() <= 0.25:
                msg = input.nick + delim + ' ' + msg
            if random.random() <= 0.15:
                chat(jenni, input)

            jenni.say(msg)
chat.rule = r'(?i)($nickname[:,]?\s)?(.*)'


def random_chat(jenni, input):
    bad_chans =  fchannels()
    if bad_chans and (input.sender).lower() in bad_chans:
        return

    temp = random.random()
    if temp <= 0.0004:
        old_input = input
        chat(jenni, old_input)
random_chat.rule = r'.*'


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


def fchannels():
    try:
        f = open('nochannels.txt', 'r')
    except:
        return False
    lines = f.readlines()[0]
    f.close()
    lines = lines.replace('\n', '')
    return lines.split(',')


if __name__ == '__main__':
    print __doc__.strip()

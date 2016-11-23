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

mycb = cleverbot.Cleverbot()

nowords = ['reload', 'help', 'tell', 'ask', 'ping']

r_entity = re.compile(r'&[A-Za-z0-9#]+;')
HTML_ENTITIES = { 'apos': "'" }
nouns = ['ZHVjaw==', 'Y2F0', 'ZG9n', 'aHVtYW4=', 'cGVyc29u', 'Y29ybg==',
         'cmF0', 'a2l0dGVu', 'ZGFuY2Vy', ]

kb_nearby = {
        'a': ['q', 'w', 's', 'z'],
        'b': ['v', 'g', 'h', 'n'],
        'c': ['x', 'd', 'f', 'v'],
        'd': ['s', 'x', 'c', 'f', 'r', 'e'],
        'e': ['w', 's', 'd', 'r'],
        'f': ['r', 'd', 'c', 'v', 'g', 't'],
        'g': ['f', 'v', 'b', 'h', 'y', 't'],
        'h': ['g', 'b', 'n', 'j', 'u', 'y'],
        'i': ['u', 'j', 'k', 'o'],
        'j': ['h', 'n', 'm', 'k', 'i', 'u'],
        'k': ['j', 'm', ',', 'l', 'o', 'i'],
        'l': ['k', 'p', 'o'],
        'm': ['n', 'j', 'k', ','],
        'n': ['b', 'h', 'j', 'm'],
        'o': ['i', 'k', 'l', ';', 'p'],
        'p': ['o', 'l', '['],
        'q': ['a', 'w', '1', '2'],
        'r': ['e', 'd', 'f', 't', '4'],
        's': ['a', 'z', 'x', 'd', 'e', 'w'],
        't': ['r', 'f', 'g', 'y', '5'],
        'u': ['y', 'h', 'j', 'i', '7'],
        'v': ['c', 'b', 'g', 'f'],
        'w': ['q', 'a', 's', 'e', '2'],
        'x': ['z', 's', 'd', 'c'],
        'y': ['t', 'g', 'h', 'u', '6'],
        'z': ['a', 's', 'x'],
}

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

    if channel.startswith('+#') or channel.startswith('@#'):
        return
    elif channel.startswith('#') and txt[0]:
        ## in a channel and prepended with jenni's name
        pm = False
        msgi = (msgi).encode('utf-8')
        try:
            time.sleep(random.randint(1, 5))
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
        msgi = (msgi).encode('utf-8')
        try:
            time.sleep(random.randint(1, 5))
            msgo = mycb.ask(msgi)
        except:
            return
    else:
        return

    if msgo:
        time.sleep(random.randint(1, 5))

        response = re.sub('(?i)clever(me|script|bot)', 'jenni', msgo)
        response = re.sub('(?i)\S+bot', (random.choice(nouns)).decode('base64'), response)
        response = re.sub('(?i)(bot|human|ai)', (random.choice(nouns)).decode('base64'), response)
        response = re.sub('(?i)computer', (random.choice(nouns)).decode('base64'), response)
        response = r_entity.sub(e, response)

        if random.random() <= 0.5:
            response = response[0].lower() + response[1:]

        if random.random() <= 0.5:
            response = response[:-1]

        def chomp(txt):
            random_int_rm = random.randint(1, len(txt))
            return txt[:random_int_rm-1] + txt[random_int_rm:]

        def switcharoo(txt):
            temp = random.randint(1, len(txt) - 2)
            return txt[:temp] + txt[temp + 1] + txt[temp] + txt[temp + 2:]

        def swaparoo(txt):
            random_to_rm = random.randint(1, len(txt) - 1)
            txt_char = txt[random_to_rm]
            new_char = txt_char
            if (txt_char).lower() in kb_nearby:
                new_char = random.choice(kb_nearby[(txt_char).lower()])
            return txt[:random_to_rm] + new_char + txt[random_to_rm + 1:]


        if random.random() <= 0.25:
            l_response = len(response) // 20
            for x in range(1, l_response):
                response = chomp(response)

        if random.random() <= 0.15:
            l_response = len(response) // 30
            for x in range(1, l_response):
                response = switcharoo(response)

        if random.random() <= 0.20:
            l_response = len(response) // 15
            for x in range(1, l_response):
                response = swaparoo(response)

        if random.random() <= 0.05:
            response = response.upper()


        if pm:
            if random.random() <= 0.04:
                return
            jenni.say(response)
            if hasattr(jenni.config, 'logchan_pm'):
                beginning = ':%s PRIVMSG %s :' % (jenni.config.nick, input.sender)
                jenni.msg(jenni.config.logchan_pm, beginning + response)
        else:
            delim = random.choice((',', ':'))
            msg = '%s' % (response)

            if random.random() <= 0.25:
                msg = input.nick + delim + ' ' + msg
            if random.random() <= 0.05:
                return

            jenni.say(msg)

    if random.random() <= 0.05:
        chat(jenni, input)

chat.rule = r'(?i)($nickname[:,]?\s)?(.*)'


def random_chat(jenni, input):
    bad_chans =  fchannels()
    if bad_chans and (input.sender).lower() in bad_chans:
        return

    if random.random() <= (1 / 2500.0):
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

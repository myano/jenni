#!/usr/bin/env python
# coding=utf-8
"""
calc.py - jenni Calculator Module
Copyright 2009-2013, Michael Yanovich (yanovich.net)
Copyright 2008-2013, Sean B. Palmer (inamidst.com)
Licensed under the Eiffel Forum License 2.

More info:
 * jenni: https://github.com/myano/jenni/
 * Phenny: http://inamidst.com/phenny/
"""

import HTMLParser
import re
from socket import timeout
import string
from modules import unicode as uc
import web


def c(jenni, input):
    """.c -- Google calculator."""
    if not input.group(2):
        return jenni.reply('Nothing to calculate.')
    q = input.group(2).encode('utf-8')
    q = q.replace('\xcf\x95', 'phi')  # utf-8 U+03D5
    q = q.replace('\xcf\x80', 'pi')  # utf-8 U+03C0
    uri = 'https://www.google.com/ig/calculator?q='
    bytes = web.get(uri + web.urllib.quote(q))
    parts = bytes.split('",')
    equation = [p for p in parts if p.startswith('{lhs: "')][0][7:]
    answer = [p for p in parts if p.startswith('rhs: "')][0][6:]
    if answer and equation:
        answer = answer.decode('unicode-escape')
        answer = ''.join(chr(ord(c)) for c in answer)
        answer = uc.decode(answer)
        answer = answer.replace(u'\xc2\xa0', ',')
        answer = answer.replace('<sup>', '^(')
        answer = answer.replace('</sup>', ')')
        answer = web.decode(answer)
        answer = answer.strip()
        equation = uc.decode(equation)
        equation = equation.strip()
        max_len = 450 - len(answer) - 6
        new_eq = equation
        if len(new_eq) > max_len:
            end = max_len - 10
            new_eq = new_eq[:end]
            new_eq += '[..]'
        output = '\x02' + answer + '\x02' + ' == ' + new_eq
        jenni.say(output)
    else:
        jenni.say('Sorry, no result.')
c.commands = ['c', 'calc']
c.example = '.c 5 + 3'


def py(jenni, input):
    """.py <code> -- evaluates python code"""
    code = input.group(2)
    if not code:
        return jenni.reply('No code provided.')
    query = code.encode('utf-8')
    uri = 'https://tumbolia.appspot.com/py/'
    answer = web.get(uri + web.urllib.quote(query))
    if answer:
        jenni.say(answer)
    else:
        jenni.reply('Sorry, no result.')
py.commands = ['py', 'python']
py.example = '.py print "Hello world, %s!" % ("James")'


def wa(jenni, input):
    """.wa <input> -- queries WolframAlpha with the given input."""
    if not input.group(2):
        return jenni.reply("No search term.")
    query = input.group(2).encode('utf-8')
    uri = 'https://tumbolia.appspot.com/wa/'
    try:
        answer = web.get(uri + web.urllib.quote(query.replace('+', '%2B')))
    except timeout as e:
        return jenni.reply("Request timd out")
    if answer:
        answer = answer.decode("string_escape")
        answer = HTMLParser.HTMLParser().unescape(answer)
        match = re.search('\\\:([0-9A-Fa-f]{4})', answer)
        if match is not None:
            char_code = match.group(1)
            char = unichr(int(char_code, 16))
            answer = answer.replace('\:' + char_code, char)
        waOutputArray = string.split(answer, ";")
        if (len(waOutputArray) < 2):
            jenni.reply(answer)
        else:
            jenni.reply(waOutputArray[0] + " = " + waOutputArray[1])
        waOutputArray = list()
    else:
        jenni.reply('Sorry, no result from WolframAlpha.')
wa.commands = ['wa', 'wolfram']
wa.example = '.wa land area of the European Union'

if __name__ == '__main__':
    print __doc__.strip()

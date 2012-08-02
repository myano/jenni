#!/usr/bin/env python
# -*- coding: utf-8 -*-
# vim: set fileencoding=UTF-8 :
"""
ham.py - Ham Radio Module
Copyright 2011, Michael Yanovich, yanovich.net
Licensed under the Eiffel Forum License 2.

More info:
 * Jenni: https://github.com/myano/jenni/
 * Phenny: http://inamidst.com/phenny/

This contains a collection of lookups and calls for ham radio enthusiasts.
"""

import re
import web

re_look = re.compile('<FONT FACE="Arial, Helvetica, sans-serif" SIZE=4>(.*)<BR>')

morse = {
        "a": ".-",
        "b": "-...",
        "c": "-.-.",
        "d": "-..",
        "e": ".",
        "f": "..-.",
        "g": "--.",
        "h": "....",
        "i": "..",
        "j": ".---",
        "k": "-.-",
        "l": ".-..",
        "m": "--",
        "n": "-.",
        "o": "---",
        "p": ".--.",
        "q": "--.-",
        "r": ".-.",
        "s": "...",
        "t": "-",
        "u": "..-",
        "v": "...-",
        "w": ".--",
        "x": "-..-",
        "y": "-.--",
        "z": "--..",
        "1": ".----",
        "2": "..---",
        "3": "...--",
        "4": "....-",
        "5": ".....",
        "6": "-....",
        "7": "--...",
        "8": "---..",
        "9": "----.",
        "0": "-----",
        " ": " ",
        ".": ".-.-.-",
        ",": "--..--",
        "?": "..--..",
        "'": ".----.",
        "!": "-.-.--",
        "/": "-..-.",
        "(": "-.--.",
        ")": "-.--.-",
        "&": ".-...",
        ":": "---...",
        ";": "-.-.-.",
        "=": "-...-",
        "+": ".-.-.",
        "-": "-....-",
        "_": "..--.-",
        '"': ".-..-.",
        "$": "...-..-",
        "@": ".--.-.",
        u"ä": ".-.-",
        u"æ": ".-.-",
        u"ą": ".-.-",
        u"à": ".--.-",
        u"å": ".--.-",
        u"ç": "-.-..",
        u"ĉ": "-.-..",
        u"ć": "-.-..",
        u"š": "----",
        u"ð": "..--.",
        u"ś": "...-...",
        u"è": ".-..-",
        u"é": "..-..",
        u"đ": "..-..",
        u"ę": "..-..",
        u"ĝ": "--.-.",
        u"ĥ": "----",
        u"ĵ": ".---.",
        u"ź": "--..-.",
        u"ñ": "--.--",
        u"ń": "--.--",
        u"ö": "---.",
        u"ø": "---.",
        u"ó": "---.",
        u"ŝ": "...-.",
        u"þ": ".--..",
        u"ü": "..--",
        u"ŭ": "..--",
        u"ż": "--..-",
        }

def reverse_lookup(v, d=morse):
    result = " "
    for k in d:
        if d[k] == v:
            result = k
    return result

def lookup(jenni, input):
    cs = input.group(2).upper()
    link = "http://www.qth.com/callsign.php?cs=" + unicode(cs)
    page = web.get(link)
    name = re_look.findall(page)
    if name:
        jenni.say("Name: " + name[0] + ", more information available at: " + link)
    else:
        jenni.say('No matches found')
lookup.commands = ['cs']
lookup.rate = 30

def cw(jenni, input):
    re_cw = re.compile("[\.\- ]+")
    re_noncw = re.compile("[^\.\- ]+")
    text = input.group(2).lower().rstrip().lstrip()
    temp = text.split(" ")
    output = str()
    if re_cw.findall(text) and not re_noncw.findall(text):
        ## MORSE
        for code in temp:
            if " " in code:
                output += " "
                code = code.replace(" ", "")
            output += reverse_lookup(code)
        output = output.upper()
    else:
        ## TEXT
        for char in text:
            try:
                output += morse[char]
            except KeyError:
                output = "Non morse code character used."
                break
            if char != " ":
                output += " "
    jenni.reply(output)
cw.commands = ['cw']
cw.rate = 15
cw.thread = True

if __name__ == '__main__':
    print __doc__.strip()


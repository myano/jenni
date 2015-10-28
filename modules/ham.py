#!/usr/bin/env python
# -*- coding: utf-8 -*-
# vim: set fileencoding=UTF-8 :
"""
ham.py - jenni Ham Radio Module
Copyright 2011-2013, Michael Yanovich (yanovich.net)
Licensed under the Eiffel Forum License 2.

More info:
 * jenni: https://github.com/myano/jenni/
 * Phenny: http://inamidst.com/phenny/

This contains a collection of lookups and calls for ham radio enthusiasts.
"""

from modules import unicode as uc
import re
import web

re_look = re.compile('(?i)<FONT FACE="Arial, Helvetica, sans-serif" SIZE=4>(.*?)<br>(.*)</tr>')
re_more = re.compile('(?i)<B>(.*?)</B></FONT></td>\n(.*</td>)')
re_tag = re.compile(r'<[^>]+>')

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

def cs(jenni, input):
    '''.cs <callsign> -- queries qth.com for call sign information'''
    cs = input.group(2).upper()
    try:
        link = "http://www.qth.com/callsign.php?cs=" + uc.decode(web.quote(cs))
    except Exception, e:
        print e
        return jenni.say('Failed to obtain data from qth.com')
    page = web.get(link)
    info = re_look.findall(page)
    more_info = re_more.findall(page)
    if info and more_info:
        info = info[0]
        name = info[0]
        name = re_tag.sub(' ', info[0]).strip()
        address = info[1].split('<br>')
        address = ', '.join(address[1:])
        address = address.strip()
        extra = dict()
        for each in more_info:
            extra[each[0].strip()] = re_tag.sub('', each[1].strip()).strip()
        response = '(%s) ' % (web.quote(cs))
        response += 'Name: %s, Address: %s. '  # More information is available at: %s'
        response = response % (uc.decode(name), uc.decode(address))
        for each in more_info:
            temp = re_tag.sub('', each[1].strip())
            if not temp:
                temp = 'N/A'
            response += '%s: %s. ' % (each[0].strip(), temp)
        response += 'More information is available at: %s' % (link)
    else:
        response = 'No matches found.'
    jenni.say(response)
cs.commands = ['cs']
cs.example = '.cs W8LT'

def cw(jenni, input):
    re_cw = re.compile("[/\.\- ]+")
    re_noncw = re.compile("[^/\.\- ]+")
    if not input.group(2):
        return jenni.say('Please provide some input.')
    text = input.group(2).lower().rstrip().lstrip()
    temp = text.split(" ")
    output = str()
    if re_cw.findall(text) and not re_noncw.findall(text):
        ## MORSE
        output = output.replace(' / ', '  ')
        for code in temp:
            if " " in code:
                output += " "
                code = code.replace(" ", "")
            output += reverse_lookup(code)
        output = output.replace('  ', ' ')
        output = output.upper()
    else:
        ## TEXT
        for char in text:
            try:
                output += morse[char]
            except KeyError:
                output = "Non morse code character used."
                break
            output += " "
    jenni.reply(output)
cw.commands = ['cw']
cw.thread = True

if __name__ == '__main__':
    print __doc__.strip()


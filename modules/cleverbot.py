#!/usr/bin/env python
"""
cleverbot.py - jenni's Cleverbot API module
Copyright 2013 Michael Yanovich (yanovich.net)
Copyright 2013 Manishrw (github.com/manishrw)
Licensed under the Eiffel Forum License 2.

More info:
 * jenni: https://github.com/myano/jenni/
 * Phenny: http://inamidst.com/phenny/

This library lets you open chat session with cleverbot (www.cleverbot.com)

Example of how to use the bindings:

>>> import cleverbot
>>> cb = cleverbot.Session()
>>> print cb.Ask('Hello there')
'Hello.'

"""

import urllib2
import hashlib
import re
from modules import unicode as uc


class ServerFullError(Exception):
    pass

ReplyFlagsRE = re.compile('<INPUT NAME=(.+?) TYPE=(.+?) VALUE="(.*?)">',
                          re.IGNORECASE | re.MULTILINE)


class Session(object):
    keylist = ['stimulus', 'start', 'sessionid', 'vText8', 'vText7', 'vText6',
               'vText5', 'vText4', 'vText3', 'vText2', 'icognoid',
               'icognocheck', 'prevref', 'emotionaloutput', 'emotionalhistory',
               'asbotname', 'ttsvoice', 'typing', 'lineref', 'fno', 'sub',
               'islearning', 'cleanslate']
    headers = dict()
    headers['User-Agent'] = 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:26.0)'
    headers['User-Agent'] += ' Gecko/20130101 Firefox/26.0'
    headers['Accept'] = 'text/html,application/xhtml+xml,application/xml;'
    headers['Accept'] += 'q=0.9,*/*;q=0.8'
    headers['Accept-Language'] = 'en-us;q=0.8,en;q=0.5'
    headers['X-Moz'] = 'prefetch'
    headers['Accept-Charset'] = 'ISO-8859-1,utf-8;q=0.7,*;q=0.7'
    headers['Referer'] = 'http://www.cleverbot.com'
    headers['Cache-Control'] = 'no-cache, no-cache'
    headers['Pragma'] = 'no-cache'

    def __init__(self):
        self.arglist = ['', 'y', '', '', '', '', '', '', '', '', 'wsf', '',
                        '', '', '', '', '', '', '', '0', 'Say', '1', 'false']
        self.MsgList = list()

    def Send(self):
        data = encode(self.keylist, self.arglist)
        digest_txt = data[9:35]
        new_hash = hashlib.md5(digest_txt).hexdigest()
        self.arglist[self.keylist.index('icognocheck')] = new_hash
        data = encode(self.keylist, self.arglist)
        req = urllib2.Request('http://www.cleverbot.com/webservicemin',
                              data, self.headers)
        f = urllib2.urlopen(req)
        reply = f.read()
        return reply

    def Ask(self, q):
        self.arglist[self.keylist.index('stimulus')] = q
        if self.MsgList:
            self.arglist[self.keylist.index('lineref')] = '!0' + str(len(
                self.MsgList) / 2)
        asw = self.Send()
        self.MsgList.append(q)
        answer = parseAnswers(asw)
        for k, v in answer.iteritems():
            try:
                self.arglist[self.keylist.index(k)] = v
            except ValueError:
                pass
        self.arglist[self.keylist.index('emotionaloutput')] = str()
        text = answer['ttsText']
        self.MsgList.append(text)
        return text


def parseAnswers(text):
    d = dict()
    keys = ['text', 'sessionid', 'logurl', 'vText8', 'vText7', 'vText6',
            'vText5', 'vText4', 'vText3', 'vText2', 'prevref', 'foo',
            'emotionalhistory', 'ttsLocMP3', 'ttsLocTXT', 'ttsLocTXT3',
            'ttsText', 'lineRef', 'lineURL', 'linePOST', 'lineChoices',
            'lineChoicesAbbrev', 'typingData', 'divert']
    values = text.split('\r')
    i = 0
    for key in keys:
        d[key] = values[i]
        i += 1
    return d


def encode(keylist, arglist):
    text = str()
    for i in range(len(keylist)):
        k = keylist[i]
        v = quote(arglist[i])
        text += '&' + k + '=' + v
    text = text[1:]
    return text

always_safe = ('ABCDEFGHIJKLMNOPQRSTUVWXYZ'
               'abcdefghijklmnopqrstuvwxyz'
               '0123456789' '_.-')


def quote(s, safe='/'):  # quote('abc def') -> 'abc%20def'
    s = uc.encode(s)
    s = uc.decode(s)
    safe += always_safe
    safe_map = dict()
    for i in range(256):
        c = chr(i)
        safe_map[c] = (c in safe) and c or ('%%%02X' % i)
    try:
        res = map(safe_map.__getitem__, s)
    except:
        return ''
    return ''.join(res)


def main():
    import sys
    cb = Session()

    q = str()
    while q != 'bye':
        try:
            q = raw_input('> ')
        except KeyboardInterrupt:
            print
            sys.exit()
        print cb.Ask(q)

if __name__ == '__main__':
    print __doc__.strip()
    main()

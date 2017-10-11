#!/usr/bin/env python
"""
unicode.py - jenni Unicode Module
Copyright 2010-2013, Michael Yanovich (yanovich.net)
Licensed under the Eiffel Forum License 2.

More info:
 * jenni: https://github.com/myano/jenni/
 * Phenny: http://inamidst.com/phenny/
"""

import re
import unicodedata
import urlparse

control_chars = ''.join(map(unichr, range(0,32) + range(127,160)))
control_char_re = re.compile(u'[%s]' % re.escape(control_chars))


def supercombiner(jenni, input):
    """.sc -- displays the infamous supercombiner"""
    s = 'u'
    for i in xrange(1, 3000):
        if unicodedata.category(unichr(i)) == "Mn":
            s += unichr(i)
        if len(s) > 100:
            break
    jenni.say(s)
supercombiner.commands = ['sc']
supercombiner.rate = 30


def decode(bit):
    try:
        if isinstance(bit, str) or isinstance(bit, unicode):
            text = bit.decode('utf-8')
        else:
            text = str()
    except UnicodeDecodeError:
        try:
            text = bit.decode('iso-8859-1')
        except UnicodeDecodeError:
            text = bit.decode('cp1252')
    return text


def encode(bit):
    try:
        if isinstance(bit, str) or isinstance(bit, unicode):
            text = bit.encode('utf-8')
        else:
            text = str()
    except UnicodeEncodeError:
        try:
            text = bit.encode('iso-8859-1')
        except UnicodeEncodeError:
            text = bit.encode('cp1252')
    return text


def urlEncodeNonAscii(b):
    return re.sub('[\x80-\xFF]', lambda c: '%%%02x' % ord(c.group(0)), b)


def iriToUri(iri):
    parts = urlparse.urlparse(iri)
    return urlparse.urlunparse(
        part.encode('idna') if parti == 1 else urlEncodeNonAscii(
            part.encode('utf-8'))
        for parti, part in enumerate(parts)
    )


def remove_control_chars(s):
    return control_char_re.sub('', s)


if __name__ == '__main__':
    print __doc__.strip()

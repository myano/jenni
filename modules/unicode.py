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

all_chars = (unichr(i) for i in xrange(0x110000))
control_chars = ''.join(map(unichr, range(0,32) + range(127,160)))
control_char_re = re.compile('[%s]' % re.escape(control_chars))


def supercombiner(jenni, input):
    """.sc -- displays the infamous supercombiner"""
    s = 'u'
    for i in xrange(1, 3000):
        if unicodedata.category(unichr(i)) == "Mn":
            s += unichr(i)
        if len(s) > 100:
            break
    s = remove_control_chars(s)
    jenni.say(s)
supercombiner.commands = ['sc']
supercombiner.rate = 30


def decode(bytes):
    try:
        if isinstance(bytes, str) or isinstance(bytes, unicode):
            text = bytes.decode('utf-8')
        else:
            text = str()
    except UnicodeDecodeError:
        try:
            text = bytes.decode('iso-8859-1')
        except UnicodeDecodeError:
            text = bytes.decode('cp1252')
    return text


def encode(bytes):
    try:
        if isinstance(bytes, str) or isinstance(bytes, unicode):
            text = bytes.encode('utf-8')
        else:
            text = str()
    except UnicodeEncodeError:
        try:
            text = bytes.encode('iso-8859-1')
        except UnicodeEncodeError:
            text = bytes.encode('cp1252')
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

#!/usr/bin/env python
# coding=utf-8
"""
translate.py - jenni Translation Module
Copyright 2009-2013, Michael Yanovich (yanovich.net)
Copyright 2008-2013, Sean B. Palmer (inamidst.com)
Licensed under the Eiffel Forum License 2.

More info:
 * jenni: https://github.com/myano/jenni/
 * Phenny: http://inamidst.com/phenny/
"""

from BeautifulSoup import BeautifulSoup
import json
import re
import time
import urllib
import urllib2
import web

r_tag = re.compile(r'<(?!!)[^>]+>')
iso639_page = web.get('https://en.wikipedia.org/wiki/List_of_ISO_639-1_codes')
soup = BeautifulSoup(iso639_page)


def translate(text, input='auto', output='en', use_proxy=False):
    raw = False
    if output.endswith('-raw'):
        output = output[:-4]
        raw = True

    opener = urllib2.build_opener()
    opener.addheaders = [(
        'User-Agent', 'Mozilla/5.0' +
        '(X11; U; Linux i686)' +
        'Gecko/20071127 Firefox/2.0.0.11'
    )]

    input, output = urllib2.quote(input), urllib2.quote(output)

    try:
        if text is not text.encode("utf-8"):
            text = text.encode("utf-8")
    except:
        pass
    text = urllib2.quote(text)
    result = opener.open('http://translate.google.com/translate_a/t?' +
                         ('client=t&sl=%s&tl=%s' % (input, output)) +
                         ('&q=%s' % text)).read()
    while ',,' in result:
        result = result.replace(',,', ',null,')
        result = result.replace('[,', '[null,')
    data = json.loads(result)

    if raw:
        return str(data), 'en-raw'

    try:
        language = data[2] # -2][0][0]
    except:
        language = '?'

    return ''.join(x[0] for x in data[0]), language

    """
    input, output = urllib.quote(input), urllib.quote(output)
    text = urllib.quote((text).decode('utf-8'))

    uri = 'https://translate.google.com/translate_a/t?'
    params = {
            'sl': input,
            'tl': output,
            'js': 'n',
            'prev': '_t',
            'hl': 'en',
            'ie': 'UTF-8',
            'text': text,
            'client': 't',
            'multires': '1',
            'sc': '1',
            'uptl': 'en',
            'tsel': '0',
            'ssel': '0',
            'otf': '1',
    }

    for x in params:
        uri += '&%s=%s' % (x, params[x])

    #print "uri", uri

    result = opener.open(uri).read()

    ## this is hackish
    ## this makes the returned data parsable by the json module
    result = result.replace(',,', ',').replace('[,', '["",')

    while ',,' in result:
        result = result.replace(',,', ',null,')
    data = json.loads(result)

    if raw:
        return str(data), 'en-raw'

    try:
        language = data[2] # -2][0][0]
    except:
        language = '?'

    if isinstance(language, list):
        try:
            language = data[-2][0][0]
        except:
            language = data[1]

    return ''.join(x[0] for x in data[0]), language
    """

def tr(jenni, context):
    """Translates a phrase, with an optional language hint."""
    input, output, phrase = context.groups()

    phrase = phrase.encode('utf-8')

    if (len(phrase) > 350) and (not context.admin):
        return jenni.reply('Phrase must be under 350 characters.')

    input = input or 'auto'
    input = input.encode('utf-8')
    output = (output or 'en').encode('utf-8')

    if input != output:
        msg, input = translate(phrase, input, output)
        if isinstance(msg, str):
            msg = msg.decode('utf-8')
        if msg:
            msg = web.decode(msg) # msg.replace('&#39;', "'")
            msg = '"%s" (%s to %s, translate.google.com)' % (msg, input, output)
        else: msg = 'The %s to %s translation failed, sorry!' % (input, output)

        jenni.reply(msg)
    else: jenni.reply('Language guessing failed, so try suggesting one!')

tr.rule = ('$nick', ur'(?:([a-z]{2}) +)?(?:([a-z]{2}|en-raw) +)?["“](.+?)["”]\? *$')
tr.example = '$nickname: "mon chien"? or $nickname: fr "mon chien"?'
tr.priority = 'low'

def tr2(jenni, input):
    """Translates a phrase, with an optional language hint."""
    if not input.group(2): return jenni.say("No input provided.")
    command = input.group(2).encode('utf-8')

    def langcode(p):
        return p.startswith(':') and (2 < len(p) < 10) and p[1:].isalpha()

    args = ['auto', 'en']

    for i in xrange(2):
        if not ' ' in command: break
        prefix, cmd = command.split(' ', 1)
        if langcode(prefix):
            args[i] = prefix[1:]
            command = cmd
    phrase = command

    if (len(phrase) > 350) and (not input.admin):
        return jenni.reply('Phrase must be under 350 characters.')

    src, dest = args
    if src != dest:
        msg, src = translate(phrase, src, dest)
        if isinstance(msg, str):
            msg = msg.decode('utf-8')
        if msg:
            msg = web.decode(msg) # msg.replace('&#39;', "'")
            msg = '"%s" (%s to %s, translate.google.com)' % (msg, src, dest)
        else: msg = 'The %s to %s translation failed, sorry!' % (src, dest)

        jenni.reply(msg)
    else: jenni.reply('Language guessing failed, so try suggesting one!')

tr2.commands = ['tr']
tr2.priority = 'low'

def mangle(jenni, input):
    phrase = input.group(2).encode('utf-8')
    for lang in ['fr', 'de', 'es', 'it', 'ja']:
        backup = phrase
        phrase, meh_lang = translate(phrase, 'en', lang)
        if not phrase:
            phrase = backup
            break
        __import__('time').sleep(0.5)

        backup = phrase
        phrase, meh_lang = translate(phrase, lang, 'en')
        if not phrase:
            phrase = backup
            break
        __import__('time').sleep(0.5)

    jenni.reply(phrase or 'ERRORS SRY')
mangle.commands = ['mangle']


def iso639(jenni, input):
    inc_text = input.group(2)
    if not inc_text:
        return jenni.say('No input provided.')
    text = (inc_text).encode('utf-8')
    col_match = soup.find('td', text=inc_text)
    if not col_match:
        return jenni.say('No matches found.')

    row = col_match.parent.parent

    if str(row).startswith('<td>'):
        row = row.parent

    row_cols = row.findAll('td')

    family = (str(row_cols[1])).decode('utf-8')
    language_name = (str(row_cols[2])).decode('utf-8')
    native_name = (str(row_cols[3])).decode('utf-8')
    iso_6391 = (str(row_cols[4])).decode('utf-8')
    iso_6392T = (str(row_cols[5])).decode('utf-8')
    iso_6392B = (str(row_cols[6])).decode('utf-8')
    iso_6393 = (str(row_cols[7])).decode('utf-8')
    iso_6396 = (str(row_cols[8])).decode('utf-8')
    notes = str(row_cols[9]).decode('utf-8')

    family = r_tag.sub('', family)
    language_name = r_tag.sub('', language_name)
    native_name = r_tag.sub('', native_name)
    iso_6391 = r_tag.sub('', iso_6391)
    iso_6392T = r_tag.sub('', iso_6392T)
    iso_6392B = r_tag.sub('', iso_6392B)
    iso_6393 = r_tag.sub('', iso_6393)
    iso_6396 = r_tag.sub('', iso_6396)
    notes = r_tag.sub('', notes)
    if not notes or len(notes) <= 1:
        notes = 'N/A'

    jenni.say(u'\x02Language Name:\x02 %s, Native name: %s, Language family: %s (639-1: %s, 639-2/T: %s, 639-2/B: %s, 639-3: %s, 639-6: %s, notes: %s)' % (language_name, native_name, family, iso_6391, iso_6392T, iso_6392B, iso_6393, iso_6396, notes))

iso639.commands = ['lang', '639']

if __name__ == '__main__':
    print __doc__.strip()


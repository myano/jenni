#!/usr/bin/env python
"""
tld.py - jenni Why Module
Copyright 2009-2013, Michael Yanovich (yanovich.net)
Licensed under the Eiffel Forum License 2.

More info:
 * jenni: https://github.com/myano/jenni/
 * Phenny: http://inamidst.com/phenny/
"""

import BeautifulSoup
import datetime as dt
import re
import urllib2
import web

BS = BeautifulSoup.BeautifulSoup

uri = 'https://en.wikipedia.org/wiki/List_of_Internet_top-level_domains'
r_tag = re.compile(r'<(?!!)[^>]+>')
r_quote = re.compile(r'\[.*?\]')

soup = False
last_updated = dt.datetime.now() - dt.timedelta(days=30)


def gettld(jenni, input):
    '''.tld .sh -- displays information about a given top level domain.'''
    global soup

    text = input.group(2)
    if not text:
        jenni.reply("You didn't provide any input.")
        return
    text = text.split()[0]
    if text and text.startswith('.'):
        text = text[1:]
    text = text.encode('utf-8')

    if (dt.datetime.now() - last_updated) >= dt.timedelta(days=14):
        ## reloads cache if data becomes too old
        reload_cache()

    if not soup:
        reload_cache()

    tlds = soup.findAll('tr', {'valign': 'top'})
    for tld in tlds:
        tld_tds = tld('td')
        out = dict()
        if not text.startswith('.'):
            text = '.' + text
        if len(tld_tds[0]('a')) > 0 and tld_tds[0]('a')[0].text == text:
            if tld_tds[1]('a') and tld_tds[1]('img'):
                out['entity'] = tld_tds[1]('a')[0].text
            else:
                out['entity'] = tld_tds[1].text
            none_avail = 'N/A'
            out['expl'] = none_avail
            if tld_tds[2].text:
                out['expl'] = tld_tds[2].text
            out['notes'] = none_avail
            out['idn'] = none_avail
            out['dnssec'] = none_avail
            out['sld'] = none_avail
            out['ipv6'] = none_avail

            if len(tld_tds) >= 7:
                out['notes'] = str(tld_tds[3])
                out['idn'] = str(tld_tds[4].text)
                out['dnssec'] = str(tld_tds[5].text)
                out['sld'] = str(tld_tds[6].text)
                if len(tld_tds) == 8:
                    out['ipv6'] = str(tld_tds[7].text)
            elif len(tld_tds) == 5:
                out['idn'] = str(tld_tds[3].text)
                out['dnssec'] = str(tld_tds[4].text)

            new_out = dict()
            for x in out:
                chomped = r_tag.sub('', out[x].strip())
                chomped = r_quote.sub('', chomped)
                if chomped == '&#160;':
                    chomped = none_avail
                try:
                    chomped = (chomped).encode('utf-8')
                except:
                    pass
                chomped = (chomped).decode('utf-8')
                new_out[x] = chomped

            return jenni.say('Entity: %s (Explanation: %s, Notes: %s). IDN: %s, DNSSEC: %s, SLD: %s, IPv6: %s' % (new_out['entity'], new_out['expl'], new_out['notes'], new_out['idn'], new_out['dnssec'], new_out['sld'], new_out['ipv6']))

    return jenni.say('No matches found for TLD: %s' % (text))

gettld.commands = ['tld']
gettld.example = '.tld .it'


def reload_cache():
    global last_updated
    global soup

    last_updated = dt.datetime.now()
    page = web.get(uri)
    soup = BS(page)


def tld_cache(jenni, input):
    jenni.say('TLD cache from Wikipedia last updated: ' + str(last_updated))

    reload_cache()

    jenni.say('TLD cache is now current.')
tld_cache.commands = ['tld-cache']


if __name__ == '__main__':
    print __doc__.strip()

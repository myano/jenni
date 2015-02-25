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
import re
import urllib2
import web

BS = BeautifulSoup.BeautifulSoup

uri = 'https://en.wikipedia.org/wiki/List_of_Internet_top-level_domains'
r_tag = re.compile(r'<(?!!)[^>]+>')
r_quote = re.compile(r'\[.*?\]')
page = web.get(uri)
soup = BS(page)


def gettld(jenni, input):
    '''.tld .sh -- displays information about a given top level domain.'''
    text = input.group(2)
    if not text:
        jenni.reply("You didn't provide any input.")
        return
    text = text.split()[0]
    if text and text.startswith('.'):
        text = text[1:]
    text = text.encode('utf-8')

    tlds = soup.findAll('tr', {'valign': 'top'})
    for tld in tlds:
        tld_tds = tld('td')
        out = dict()
        if not text.startswith('.'):
            text = '.' + text
        if len(tld_tds[0]('a')) > 0 and tld_tds[0]('a')[0].text == text:
            if tld_tds[1]('a') and tld_tds[1]('img'):
                out['entity'] = str(tld_tds[1]('a')[0].text)
            else:
                out['entity'] = str(tld_tds[1].text)
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
                chomped = (chomped).decode('utf-8')
                new_out[x] = chomped

            return jenni.say('Entity: %s (Explanation: %s, Notes: %s). IDN: %s, DNSSEC: %s, SLD: %s, IPv6: %s' % (new_out['entity'], new_out['expl'], new_out['notes'], new_out['idn'], new_out['dnssec'], new_out['sld'], new_out['ipv6']))

    return jenni.say('No matches found for TLD: %s' % (text))

gettld.commands = ['tld']
gettld.example = '.tld .it'

if __name__ == '__main__':
    print __doc__.strip()

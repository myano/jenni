#!/usr/bin/env python
"""
tld.py - jenni Why Module
Copyright 2009-2013, Michael Yanovich (yanovich.net)
Licensed under the Eiffel Forum License 2.

More info:
 * jenni: https://github.com/myano/jenni/
 * Phenny: http://inamidst.com/phenny/
"""

import re
import urllib2
import web

uri = 'https://en.wikipedia.org/wiki/List_of_Internet_top-level_domains'
r_tag = re.compile(r'<(?!!)[^>]+>')
page = web.get(uri)

search_1 = r'(?i)<a href="\S+" title="[\S ]+">\.{0}</a></td>\n(<td><a href=".*</a></td>\n)?<td>([A-Za-z0-9].*?)</td>\n<td>(.*)</td>\n<td[^>]*>(.*?)</td>\n<td[^>]*>(.*?)</td>\n'
search_2 = r'(?i)<a href="\S+" title="([\S ]+)">\.{0}</a></td>\n<td><a href=".*">(.*)</a></td>\n<td>([A-Za-z0-9].*?)</td>\n<td[^>]*>(.*?)</td>\n<td[^>]*>(.*?)</td>\n'
search_3 = r'<a href="\S+" title="[\S ]+">.{0}</a></td>\n<td><span class="flagicon"><img.*?\">(.*?)</a></td>\n<td[^>]*>(.*?)</td>\n<td[^>]*>(.*?)</td>\n<td[^>]*>(.*?)</td>\n<td[^>]*>(.*?)</td>\n<td[^>]*>(.*?)</td>\n'


def gettld(jenni, input):
    '''.tld .sh -- displays information about a given top level domain.'''
    text = input.group(2)
    if text and text.startswith('.'):
        text = text[1:]
    if not text:
        jenni.reply("You didn't provide any input.")
        return
    search = search_1
    search = search.format(text)
    re_country = re.compile(search)
    matches = re_country.findall(page)
    if not matches:
        search = search_2
        search = search.format(text)
        re_country = re.compile(search)
        matches = re_country.findall(page)
    if matches:
        matches = list(matches[0])
        i = 0
        while i < len(matches):
            matches[i] = r_tag.sub('', matches[i])
            i += 1
        desc = matches[2]
        if len(desc) > 400:
            desc = desc[:400] + '...'
        reply = '%s -- %s. IDN: %s, DNSSEC: %s' % (matches[1], desc,
                matches[3], matches[4])
        jenni.reply(reply)
    else:
        search = search_3
        search = search.format(unicode(text))
        re_country = re.compile(search)
        matches = re_country.findall(page)
        if matches:
            matches = matches[0]
            dict_val = dict()
            dict_val['country'], dict_val['expl'], dict_val['notes'], \
                dict_val['idn'], dict_val['dnssec'], \
                dict_val['sld'] = matches
            for key in dict_val:
                if dict_val[key] == '&#160;':
                    dict_val[key] = 'N/A'
                dict_val[key] = re.sub('\[.*\]', '', dict_val[key])
                dict_val[key] = r_tag.sub('', dict_val[key])
            if len(dict_val['notes']) > 400:
                dict_val['notes'] = dict_val['notes'][:400] + '...'
            reply = '%s (%s, %s). IDN: %s, DNSSEC: %s, SLD: %s' % (
                    dict_val['country'], dict_val['expl'], dict_val['notes'],
                    dict_val['idn'], dict_val['dnssec'], dict_val['sld'])
        else:
            reply = 'No matches found for TLD: {0}'.format(unicode(text))
        jenni.reply(reply)
gettld.commands = ['tld']
gettld.example = '.tld .it'
gettld.rate = 3

if __name__ == '__main__':
    print __doc__.strip()

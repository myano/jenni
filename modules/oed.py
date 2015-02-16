#!/usr/bin/env python
'''
oed.py - OED Module
Copyright 2014 Sujeet Akula (sujeet@freeboson.org)
Licensed under the Eiffel Forum License 2.

More info:
 * jenni-misc: https://github.com/freeboson/jenni-misc/
 * jenni: https://github.com/myano/jenni/
 * Phenny: http://inamidst.com/phenny/

NOTE: if your bot is not run on an IP that has access to OED, you should disable
this module. (todo: add support for ezproxy library login)
'''

from lxml import etree
from StringIO import StringIO
import web
from HTMLParser import HTMLParser
import re, sys


oed = r'http://www.oed.com/srupage'
oed_url = r'http://www.oed.com/srupage?operation=searchRetrieve&query=cql.serverChoice+=+{}&maximumRecords=100&startRecord=1'
srw = r'{http://www.loc.gov/zing/srw/}'
sru_dc = r'{info:srw/schema/1/dc-v1.1}'
dc = r'{http://purl.org/dc/elements/1.1/}'



#quick and dirty
rm_disp = re.compile(r'<[/]*display>')
rm_span = re.compile(r'<[/]*span[^>]*>')
sub_em = re.compile(r'<[/]*em>')
sub_strong = re.compile(r'<[/]*strong>')

hparse = HTMLParser()


def search(query):
    defs = list()

    result_xml = web.get(oed_url.format(web.urllib.quote(query)))

    result_tree = etree.parse(StringIO(result_xml))
    root = result_tree.getroot()

    num_records = root.find(srw + 'numberOfRecords')
    if num_records is None:
        return
    else:
        num_records = int(num_records.text)

    if num_records < 1:
        return

    records = root.find(srw + 'records').getiterator()

    for record in records:
        rdata = record.find(srw + 'recordData')
        if rdata is not None:
            data = rdata.find(sru_dc + 'dc')
            title = hparse.unescape(data.find(dc + 'title').text).encode('utf-8')
            desc = hparse.unescape(clean_desc(data.find(dc + 'description').text.encode('utf-8')))
            defs.append(title + ' :: ' + desc)

    return (num_records, defs)

def clean_desc(desc):
    desc = rm_disp.sub('', desc)
    desc = rm_span.sub('', desc)
    desc = sub_em.sub('/', desc)
    desc = sub_strong.sub('\x02', desc)
    return desc

def oed(jenni, input):
    '''.oed -- Look up definitions in the Oxford English Dictionary'''
    word = input.group(2)

    try:
        (num, defns) = search(word)
    except:
        jenni.say("[OED] Couldn't look up " + word + '.')
        return

    if num < 1 or len(defns) < 1:
        jenni.say("[OED] No results for " + word + '.')
        return

    long_def = "[OED] " + str(num) + " record(s). " + " | ".join(defns[:10])
    if len(long_def) > 300:
        long_def = long_def[:295] + '[...]'

    jenni.say(long_def)

oed.commands = ['oed']
oed.priority = 'high'



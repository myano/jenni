#!/usr/bin/env python
'''
arXiv.py -- arXiv Module
Copyright 2014 Sujeet Akula (sujeet@freeboson.org)
Licensed under the Eiffel Forum License 2.

More info:
 * jenni-misc: https://github.com/freeboson/jenni-misc/
 * jenni: https://github.com/myano/jenni/
 * Phenny: http://inamidst.com/phenny/
'''

import web, re, feedparser
from web import urllib
from modules.url import short

# Base api query url
base_url = 'http://export.arxiv.org/api/query?';

request = 'search_query={}&start=0&max_results=1'

feedparser._FeedParserMixin.namespaces['http://a9.com/-/spec/opensearch/1.1/'] = 'opensearch'
feedparser._FeedParserMixin.namespaces['http://arxiv.org/schemas/atom'] = 'arxiv'

id_filter = re.compile(r'.*\/abs\/((?:[\d\.]{9})|(?:[\w\-\.]*\/\d{7}))(?:v\d+){,1}[/]{,1}') # id will be in \1 
collab_check = re.compile(r'\s(?:Collaboration)|(?:Group).*', flags=re.IGNORECASE)
no_http = re.compile(r'.*\/\/(.*)')
no_newlines = re.compile(r'\n')

def get_arxiv(query):

    url = base_url + request.format(urllib.quote(query))
    xml = web.get(url)
    feed = feedparser.parse(xml)

    if feed.feed.opensearch_totalresults < 1:
        raise IndexError

    # get the first (and only) entry
    entry = feed.entries[0]

    abs_link = entry.id
    arxivid = id_filter.sub(r'\1', abs_link)

    try:
        short_url = short(abs_link)[0][1]
    except:
        short_url = ''

    # format the author string
    # use et al. for 3+ authors
    if len(entry.authors) > 2:
        authors = entry.authors[0].name

        if collab_check.match(authors) is None:
            authors += ' et al.'

    elif len(entry.authors) >0:
        authors = ' and '.join([author.name for author in entry.authors])
    else:
        authors = ''

    title = entry.title
    abstract = no_newlines.sub(' ', entry.summary)

    return (arxivid, authors, title, abstract, short_url)

def summary(jenni, input):

    query = input.group(2)

    if not query:
        return jenni.say('Please provide an input to lookup via arXiv.')

    try:
        (arxivid, authors, title, abstract, url) = get_arxiv(query)
    except:
        return jenni.say("[arXiv] Could not lookup " + query + " in the arXiv.")

    arxiv_summary = "[arXiv:" + arxivid + "] " + authors + ', "' \
                    + title + '" :: ' + abstract

    long_summary = arxiv_summary + " " + url
    if len(long_summary) > 300:
        ending = '[...] ' + url
        clipped = arxiv_summary[:(300-len(ending))] + ending
    else:
        clipped = long_summary

    jenni.say(clipped)

summary.commands = ['arxiv']
summary.priority = 'high'

if __name__ == '__main__':
    print __doc__.strip()

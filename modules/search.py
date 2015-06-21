#!/usr/bin/env python
"""
search.py - jenni Web Search Module
Copyright 2009-2013, Michael Yanovich (yanovich.net)
Copyright 2013, Edward Powell (embolalia.net)
Copyright 2008-2013 Sean B. Palmer (inamidst.com)
Licensed under the Eiffel Forum License 2.

More info:
 * jenni: https://github.com/myano/jenni/
 * Phenny: http://inamidst.com/phenny/
"""

import json
import re
import urllib
import web

r_tag = re.compile(r'<(?!!)[^>]+>')


def remove_spaces(x):
    if '  ' in x:
        x = x.replace('  ', ' ')
        return remove_spaces(x)
    else:
        return x


class Grab(web.urllib.URLopener):
    def __init__(self, *args):
        self.version = 'Mozilla/5.0 (Windows NT 6.1; rv:24.0) Gecko/20100101 Firefox/24.0'
        web.urllib.URLopener.__init__(self, *args)
        self.addheader('Referer', 'https://github.com/myano/jenni')
        self.addheader('Accept', '*/*')
    def http_error_default(self, url, fp, errcode, errmsg, headers):
        return web.urllib.addinfourl(fp, [headers, errcode], "http:" + url)

def google_ajax(query):
    """Search using AjaxSearch, and return its JSON."""
    if isinstance(query, unicode):
        query = query.encode('utf-8')
    uri = 'https://ajax.googleapis.com/ajax/services/search/web'
    args = '?v=1.0&safe=off&q=' + web.urllib.quote(query)
    handler = web.urllib._urlopener
    web.urllib._urlopener = Grab()
    bytes = web.get(uri + args)
    web.urllib._urlopener = handler
    return json.loads(bytes)

def google_search(query):
    results = google_ajax(query)
    try: return results['responseData']['results'][0]['unescapedUrl']
    except IndexError: return None
    except TypeError:
        print results
        return False

def google_count(query):
    results = google_ajax(query)
    if not results.has_key('responseData'): return '0'
    if not results['responseData'].has_key('cursor'): return '0'
    if not results['responseData']['cursor'].has_key('estimatedResultCount'):
        return '0'
    return results['responseData']['cursor']['estimatedResultCount']

def formatnumber(n):
    """Format a number with beautiful commas."""
    parts = list(str(n))
    for i in range((len(parts) - 3), 0, -3):
        parts.insert(i, ',')
    return ''.join(parts)

def g(jenni, input):
    """Queries Google for the specified input."""
    query = input.group(2)
    if not query:
        return jenni.reply('.g what?')
    query = query.encode('utf-8')
    uri = google_search(query)
    if uri:
        if 'wikipedia.org/' in uri:
            uri = uri.replace('http:', 'https:')
        jenni.reply(uri)
        if not hasattr(jenni, 'last_seen_uri'):
            jenni.last_seen_uri = {}
        jenni.last_seen_uri[input.sender] = uri
    elif uri is False: jenni.reply("Problem getting data from Google.")
    else: jenni.reply("No results found for '%s'." % query)
g.commands = ['g']
g.priority = 'high'
g.example = '.g swhack'

def gc(jenni, input):
    """Returns the number of Google results for the specified input."""
    query = input.group(2)
    if not query:
        return jenni.reply('.gc what?')
    query = query.encode('utf-8')
    num = formatnumber(google_count(query))
    jenni.say(query + ': ' + num)
gc.commands = ['gc']
gc.priority = 'high'
gc.example = '.gc extrapolate'

r_query = re.compile(
    r'\+?"[^"\\]*(?:\\.[^"\\]*)*"|\[[^]\\]*(?:\\.[^]\\]*)*\]|\S+'
)

def gcs(jenni, input):
    if not input.group(2):
        return jenni.reply("Nothing to compare.")
    queries = r_query.findall(input.group(2))
    if len(queries) > 6:
        return jenni.reply('Sorry, can only compare up to six things.')

    results = []
    for i, query in enumerate(queries):
        query = query.strip('[]')
        query = query.encode('utf-8')
        n = int((formatnumber(google_count(query)) or '0').replace(',', ''))
        results.append((n, query))
        if i >= 2: __import__('time').sleep(0.25)
        if i >= 4: __import__('time').sleep(0.25)

    results = [(term, n) for (n, term) in reversed(sorted(results))]
    reply = ', '.join('%s (%s)' % (t, formatnumber(n)) for (t, n) in results)
    jenni.say(reply)
gcs.commands = ['gcs', 'comp']

r_bing = re.compile(r'<h3><a href="([^"]+)"')

def bing_search(query, lang='en-GB'):
    query = web.urllib.quote(query)
    base = 'http://www.bing.com/search?mkt=%s&q=' % lang
    bytes = web.get(base + query)
    m = r_bing.search(bytes)
    if m: return m.group(1)

def bing(jenni, input):
    """Queries Bing for the specified input."""
    query = input.group(2)
    if query.startswith(':'):
        lang, query = query.split(' ', 1)
        lang = lang[1:]
    else: lang = 'en-GB'
    if not query:
        return jenni.reply('.bing what?')

    query = query.encode('utf-8')
    uri = bing_search(query, lang)
    if uri:
        jenni.reply(uri)
        if not hasattr(jenni, 'last_seen_uri'):
            jenni.last_seen_uri = {}
        jenni.last_seen_uri[input.sender] = uri
    else: jenni.reply("No results found for '%s'." % query)
bing.commands = ['bing']
bing.example = '.bing swhack'


def duck_sanitize(incoming):
    return web.decode((incoming).decode('utf-8'))


def duck_zero_click_scrape(html):
    '''Scrape DDG HTML page for Zero-Click'''
    try:
        ## prefer to use BeautifulSoup
        from BeautifulSoup import BeautifulSoup
    except:
        ## if BS is not available, just fail out here
        return str()

    soup = BeautifulSoup(html)
    zero_click = str()
    if soup('div', {'class': 'zero-click-result'}):
        zero_click = str(soup('div', {'class': 'zero-click-result'})[0])
    output = r_tag.sub('', zero_click).strip()
    output = output.replace('\n', '').replace('\t', '')
    output = remove_spaces(output)
    return output


def duck_search(query):
    '''Do a DuckDuckGo Search'''

    ## grab results from the API for the query
    duck_api_results = duck_api(query)

    ## output is a string of the URL result

    ## try to find the first result
    if 'Results' in duck_api_results and min_size('Results', duck_api_results):
        ## 'Results' is the most common place to look for the first result
        output = duck_api_results['Results'][0]['FirstURL']
    elif 'AbstractURL' in duck_api_results and min_size('AbstractURL', duck_api_results):
        ## if there is no 'result', let's try AbstractURL
        ## this is usually a wikipedia article
        output = duck_api_results['AbstractURL']
    elif 'RelatedTopics' in duck_api_results and min_size('RelatedTopics', duck_api_results):
        ## if we still can't find a search result, let's grab a topic URL
        ## this is usually vaguely related to the search query
        ## many times this is a wikipedia result
        for topic in duck_api_results['RelatedTopics']:
            output = '%s - %s' % (topic['Name'], topic['Topics'][0]['FirstURL'])
            if 'duckduckgo.com' in output:
                ## as a last resort, DuckDuckGo will provide links to the query on its site
                ## it doesn't appear to ever return a https URL
                output = output.replace('http://', 'https://')
            break
    else:
        ## if we still can't find a search result via the API
        ## let's try scraping the html page
        uri = 'https://duckduckgo.com/html/?q=%s&kl=us-en&kp=-1' % web.urllib.quote(query)
        page = web.get(uri)
        r_duck = re.compile(r'nofollow" class="[^"]+" href="(.*?)">')
        m = r_duck.findall(page)
        output = str()
        if m:
            for result in m:
                if '/y.js?' not in result and '//ad.ddg.gg/' not in result and '.msn.com/' not in result:
                    ## ignore ads
                    output = result
                    break
        else:
            ## if we absolustely can't find a URL, let's try scraping the HTML
            ## page for a zero_click info
            output = duck_zero_click_scrape(page)
    return duck_sanitize(output)

def min_size(key, dictt):
    ## I am lazy
    return len(dictt[key]) > 0

def duck_api(query):
    '''Send 'query' to DDG's API and return results as a dictionary'''
    query = web.urllib.quote(query)
    uri = 'https://api.duckduckgo.com/?q=%s&format=json&no_html=1&no_redirect=1&kp=-1' % query
    results = web.get(uri)
    results = json.loads(web.get(uri))
    return results

def duck_zero_click_api(query):
    output = list()
    header = 'Zero Click: '
    results = duck_api(query)
    ## look for any possible Zero Click answers
    if 'Redirect' in results and min_size('Redirect', results):
        ## this is used when it is a !bang
        output.append(results['Redirect'].strip())
    if 'AbstractText' in results and min_size('AbstractText', results):
        ## topic summary (with no HTML)
        output.append(header + results['AbstractText'].strip())
    if 'Answer' in results and min_size('Answer', results):
        output.append(header + results['Answer'].strip())
    if 'Definition' in results and min_size('Definition', results):
        output.append(header + results['Definition'].strip())
    if not output:
        ## if we can't find anything in the API for Zero-Click
        ## give up
        return None

    return output

def duck(jenni, input):
    '''Perform a DuckDuckGo Search and Zero-Click lookup'''
    query = input.group(2)
    if not query:
        return jenni.reply('.ddg what?')

    query = query.encode('utf-8')

    ## try to find a search result via the API
    uri = duck_search(query)
    if uri:
        jenni.say(uri)
        if hasattr(jenni, 'last_seen_uri') and input.sender in jenni.last_seen_uri:
            jenni.last_seen_uri[input.sender] = uri

    ## try to find any Zero-Click stuff
    result = duck_zero_click_api(query)

    if result and len(result) == 1:
        if hasattr(jenni, 'last_seen_uri') and input.sender in jenni.last_seen_uri:
            jenni.last_seen_uri[input.sender] = result[0]

    ## loop through zero-click results
    if result and len(result) >= 1:
        k = 0
        for each in result:
            if len(each) > 0:
                jenni.say(remove_spaces(each))
                k += 1
                if k > 3:
                    ## only show 3 zero-click results
                    ## we don't want to be too spammy
                    break

    ## if we didn't get a search result
    ## nor did we get a Zero-Click result
    ## fail
    if not uri and (not result or not len(result) >= 1):
        return jenni.reply("No results found for '%s'." % query)
duck.commands = ['duck', 'ddg']

def search(jenni, input):
    if not input.group(2):
        return jenni.reply('.search for what?')
    query = input.group(2).encode('utf-8')
    gu = google_search(query) or '-'
    bu = bing_search(query) or '-'
    du = duck_search(query) or '-'

    if (gu == bu) and (bu == du):
        result = '%s (g, b, d)' % gu
    elif (gu == bu):
        result = '%s (g, b), %s (d)' % (gu, du)
    elif (bu == du):
        result = '%s (b, d), %s (g)' % (bu, gu)
    elif (gu == du):
        result = '%s (g, d), %s (b)' % (gu, bu)
    else:
        if len(gu) > 250: gu = '(extremely long link)'
        if len(bu) > 150: bu = '(extremely long link)'
        if len(du) > 150: du = '(extremely long link)'
        result = '%s (g), %s (b), %s (d)' % (gu, bu, du)

    jenni.reply(result)
search.commands = ['search']

def suggest(jenni, input):
    if not input.group(2):
        return jenni.reply("No query term.")
    query = input.group(2).encode('utf-8')
    uri = 'http://websitedev.de/temp-bin/suggest.pl?q='
    answer = web.get(uri + web.urllib.quote(query).replace('+', '%2B'))
    if answer:
        jenni.say(answer)
    else: jenni.reply('Sorry, no result.')
suggest.commands = ['suggest']

if __name__ == '__main__':
    print __doc__.strip()

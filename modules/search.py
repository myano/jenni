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
from modules import proxy

r_tag = re.compile(r'<(?!!)[^>]+>')
r_bing = re.compile(r'<h2><a href="([^"]+)"')


def remove_spaces(x):
    if '  ' in x:
        x = x.replace('  ', ' ')
        return remove_spaces(x)
    else:
        return x


def bing_search(query, lang='en-GB'):
    query = web.urllib.quote(query)
    base = 'https://www.bing.com/search?mkt=%s&q=' % lang
    page = proxy.get(base + query)
    m = r_bing.search(page)
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
        jenni.say(uri)
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
        uri = 'https://duckduckgo.com/html/?q=%s&kl=us-en&kp=-1' % query #web.urllib.quote(query)
        #page = web.get(uri)
        page = proxy.get(uri)

        r_duck = re.compile(r'nofollow" class="[^"]+" href="(.*?)">')

        bad_results = ['/y.js?', '//ad.ddg.gg/', '.msn.com/', 'r.search.yahoo.com/',]
        m = r_duck.findall(page)
        output = str()
        if m:
            for result in m:
                valid_result = True
                for each in bad_results:
                    if each in result:
                        valid_result = False
                if valid_result:
                    output = result
                    break
        else:
            ## if we absolustely can't find a URL, let's try scraping the HTML
            ## page for a zero_click info
            return((duck_zero_click_scrape(page), False))

    return((duck_sanitize(output), True))

def min_size(key, dictt):
    ## I am lazy
    return len(dictt[key]) > 0


def duck_api(query):
    '''Send 'query' to DDG's API and return results as a dictionary'''
    #query = web.urllib.quote(query)
    uri = 'https://api.duckduckgo.com/?q=%s&format=json&no_html=1&no_redirect=1&kp=-1' % query
    results = proxy.get(uri)
    results = json.loads(results)
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

    #query = query.encode('utf-8')
    #jenni.say('query: ' + query)

    ## try to find a search result via the API
    uri, only_url = duck_search(query)
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
duck.commands = ['duck', 'ddg', 'g', 'search']


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

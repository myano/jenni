#!/usr/bin/env python
# coding=utf-8
"""
calc.py - jenni Calculator Module
Copyright 2009-2013, Michael Yanovich (yanovich.net)
Copyright 2008-2013, Sean B. Palmer (inamidst.com)
Licensed under the Eiffel Forum License 2.

More info:
 * jenni: https://github.com/myano/jenni/
 * Phenny: http://inamidst.com/phenny/
"""

import HTMLParser
import json
import re
import string
import urllib
import web

from modules import unicode as uc


c_pattern = r'(?ims)<(?:h2 class="r"|div id="aoba")[^>]*>(.*?)</(?:h2|div)>'
c_answer = re.compile(c_pattern)
r_tag = re.compile(r'<(?!!)[^>]+>')
WAKEY_NOTFOUND = "Please sign up for WolframAlpha's API to use this function. http://products.wolframalpha.com/api/"

try:
    from modules import proxy
except:
    pass


def clean_up_answer(answer):
    answer = answer.encode('utf-8')
    answer = answer.decode('utf-8')
    answer = ''.join(chr(ord(c)) for c in answer)
    answer = uc.decode(answer)
    answer = answer.replace('<sup>', '^(')
    answer = answer.replace('</sup>', ')')
    answer = web.decode(answer)
    answer = answer.strip()
    answer += ' [GC]'
    return answer


def c(jenni, input):
    '''.c -- Google calculator.'''

    ## let's not bother if someone doesn't give us input
    if not input.group(2):
        return jenni.reply('Nothing to calculate.')

    ## handle some unicode conversions
    q = input.group(2).encode('utf-8')
    q = q.replace('\xcf\x95', 'phi')  # utf-8 U+03D5
    q = q.replace('\xcf\x80', 'pi')  # utf-8 U+03C0
    temp_q = q.replace(' ', '')

    ## Attempt #1 (Google)
    uri_base = 'https://www.google.com/search?gbv=1&q='
    uri = uri_base + web.urllib.quote(temp_q)

    ## To the webs!
    page = str()
    try:
        page = proxy.get(uri)
    except:
        ## if we can't access Google for calculating
        ## let us try with good ole' web.get
        page = web.get(uri)

    answer = False

    if page:
        ## if we get a response from Google
        ## let us parse out an equation from Google Search results
        answer = c_answer.findall(page)

    if answer:
        ## if the regex finding found a match we want the first result
        answer = answer[0]
        answer = clean_up_answer(answer)
        jenni.say(answer)
    else:
        #### Attempt #1a
        uri = uri_base + web.urllib.quote(q)
        try:
            page = proxy.get(uri)
        except:
            page = web.get(uri)

        answer = False

        if page:
            answer = c_answer.findall(page)

        if answer:
            answer = answer[0]
            answer = clean_up_answer(answer)
            jenni.say(answer)
        else:
            #### Attempt #2 (DuckDuckGo's API)
            ddg_uri = 'https://api.duckduckgo.com/?format=json&q='
            ddg_uri += urllib.quote(q)

            ## Try to grab page (results)
            ## If page can't be accessed, we shall fail!
            try:
                page = proxy.get(ddg_uri)
            except:
                page = web.get(ddg_uri)

            ## Try to take page source and json-ify it!
            try:
                json_response = json.loads(page)
            except:
                ## if it can't be json-ified, then we shall fail!
                json_response = None

            ## Check for 'AnswerType' (stolen from search.py)
            ## Also 'fail' to None so we can move on to Attempt #3
            if (not json_response) or (hasattr(json_response, 'AnswerType') and json_response['AnswerType'] != 'calc'):
                answer = None
            else:
                ## If the json contains an Answer that is the result of 'calc'
                ## then continue
                answer = json_response['Answer']
                if hasattr(answer, 'result'):
                    answer = answer['result']
                parts = answer.split('</style>')
                answer = ''.join(parts[1:])
                answer = re.sub(r'<.*?>', '', answer).strip()

            if answer:
                ## If we have found answer with Attempt #2
                ## go ahead and display it
                answer += ' [DDG API]'
                return jenni.say(answer)

            else:
                #### Attempt #3 (Wolfram Alpha)
                if not hasattr(jenni.config, 'wolframalpha_apikey'):
                    return jenni.say(WAKEY_NOTFOUND)

                answer = get_wa(q, jenni.config.wolframalpha_apikey)

                return jenni.say(answer + ' [WA]')

c.commands = ['c', 'cal', 'calc']
c.example = '.c 5 + 3'


def py(jenni, input):
    """.py <code> -- evaluates python code"""
    code = input.group(2)
    if not code:
        return jenni.reply('No code provided.')
    query = code.encode('utf-8')
    uri = 'https://tumbolia-two.appspot.com/py/'
    try:
        answer = web.get(uri + web.urllib.quote(query))
        if answer is not None and answer != "\n":
            jenni.say(answer)
        else:
            jenni.reply('Sorry, no result.')
    except Exception, e:
        jenni.reply('The server did not return an answer.')
py.commands = ['py', 'python']
py.example = '.py print "Hello world, %s!" % ("James")'


def math(jenni, input):
    if not input.group(2):
        return jenni.reply("No search term.")

    txt = input.group(2)
    txt = txt.encode('utf-8')
    txt = txt.decode('utf-8')
    txt = txt.encode('utf-8')
    txt = urllib.quote(txt.replace('+', '%2B'))

    url = 'http://gamma.sympy.org/input/?i='

    re_answer = re.compile(r'<script type="\S+; mode=display".*?>(.*?)</script>')

    page = proxy.get(url + txt)

    results = re_answer.findall(page)

    if results:
        jenni.say(results[0])
    else:
        jenni.say('No results found on gamma.sympy.org!')
math.commands = ['math']


def get_wa(search, appid):
    txt = search
    txt = txt.decode('utf-8')
    txt = txt.encode('utf-8')
    txt = urllib.quote(txt)

    uri = 'https://api.wolframalpha.com/v2/query?reinterpret=true&appid=' + appid
    uri += '&input=' + txt

    page = proxy.get(uri)

    try:
        from bs4 import BeautifulSoup
    except ImportError:
        return "Please install 'bs4', also known as BeautifulSoup via pip to use WolframAlpha."

    soup = BeautifulSoup(page, 'xml')
    attempt_one = soup.find_all(attrs={'primary':'true'})

    answer = 'No answers found!'

    if attempt_one:
        answer = attempt_one[0].plaintext.get_text()
        if not answer:
            answer = attempt_one[0].imagesource.get_text()
    else:
        for pod in soup.find_all('pod'):
            if pod.get('title') != 'Input interpretation' and pod.plaintext.get_text():
                answer = pod.plaintext.get_text()
                break
    return answer


def wa(jenni, input):
    if not hasattr(jenni.config, 'wolframalpha_apikey'):
        return jenni.say(WAKEY_NOTFOUND)

    appid = jenni.config.wolframalpha_apikey

    if not input.group(2):
        return jenni.reply("No search term.")

    txt = input.group(2)
    txt = txt.encode('utf-8')
    txt = txt.decode('utf-8')
    txt = txt.encode('utf-8')

    result = get_wa(txt, appid)

    if not result:
        return jenni.say("No results found.")

    return jenni.say(result)
wa.commands = ['wa']

if __name__ == '__main__':
    print __doc__.strip()

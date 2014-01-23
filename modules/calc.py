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

from modules import search
from modules import unicode as uc
from socket import timeout


c_pattern = r'(?ims)<(?:h2 class="r"|div id="aoba")[^>]*>(.*?)</(?:h2|div)>'
c_answer = re.compile(c_pattern)
r_tag = re.compile(r'<(?!!)[^>]+>')


def c(jenni, input):
    '''.c -- Google calculator.'''

    ## let's not bother if someone doesn't give us input
    if not input.group(2):
        return jenni.reply('Nothing to calculate.')

    ## handle some unicode conversions
    q = input.group(2).encode('utf-8')
    q = q.replace('\xcf\x95', 'phi')  # utf-8 U+03D5
    q = q.replace('\xcf\x80', 'pi')  # utf-8 U+03C0

    ## Attempt #1 (Google)
    uri = 'https://www.google.com/search?gbv=1&q='
    uri += web.urllib.quote(q)

    ## To the webs!
    try:
        page = web.get(uri)
    except:
        ## if we can't access Google for calculating
        ## let us move on to Attempt #2
        page = None
        answer = None

    if page:
        ## if we get a response from Google
        ## let us parse out an equation from Google Search results
        answer = c_answer.findall(page)

    if answer:
        ## if the regex finding found a match we want the first result
        answer = answer[0]
        #answer = answer.replace(u'\xc2\xa0', ',')
        answer = answer.decode('unicode-escape')
        answer = ''.join(chr(ord(c)) for c in answer)
        answer = uc.decode(answer)
        answer = answer.replace('<sup>', '^(')
        answer = answer.replace('</sup>', ')')
        answer = web.decode(answer)
        answer = answer.strip()
        jenni.say(answer)
    else:
        #### Attempt #2 (DuckDuckGo's API)
        ddg_uri = 'https://api.duckduckgo.com/?format=json&q='
        ddg_uri += urllib.quote(q)

        ## Try to grab page (results)
        ## If page can't be accessed, we shall fail!
        try:
            page = web.get(ddg_uri)
        except:
            page = None

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
            answer = re.sub(r'\<.*?\>', '', json_response['Answer']).strip()

        if answer:
            ## If we have found answer with Attempt #2
            ## go ahead and display it
            jenni.say(answer)
        else:
            #### Attempt #3 (DuckDuckGo's HTML)
            ## This relies on BeautifulSoup; if it can't be found, don't even bother
            try:
                from BeautifulSoup import BeautifulSoup
            except:
                return jenni.say('No results. (Please install BeautifulSoup for additional checking.)')

            ddg_html_page = web.get('https://duckduckgo.com/html/?q=%s&kl=us-en&kp=-1' % (web.urllib.quote(q)))
            soup = BeautifulSoup(ddg_html_page)

            ## use BeautifulSoup to parse HTML for an answer
            zero_click = str()
            if soup('div', {'class': 'zero-click-result'}):
                zero_click = str(soup('div', {'class': 'zero-click-result'})[0])

            ## remove some excess text
            output = r_tag.sub('', zero_click).strip()
            output = output.replace('\n', '').replace('\t', '')

            ## test to see if the search module has 'remove_spaces'
            ## otherwise, let us fail
            try:
                output = search.remove_spaces(output)
            except:
                output = str()

            if output:
                ## If Attempt #3 worked, display the answer
                jenni.say(output)
            else:
                ## If we made it this far, we have tried all available resources
                jenni.say('Absolutely no results!')
c.commands = ['c', 'cal', 'calc']
c.example = '.c 5 + 3'


def py(jenni, input):
    """.py <code> -- evaluates python code"""
    code = input.group(2)
    if not code:
        return jenni.reply('No code provided.')
    query = code.encode('utf-8')
    uri = 'https://tumbolia.appspot.com/py/'
    try:
        answer = web.get(uri + web.urllib.quote(query))
        if answer is not None and answer != "\n":
            jenni.say(answer)
        else:
            jenni.reply('Sorry, no result.')
    except Exception, e:
        jenni.reply('The server did not return an answer.')
        print '[.py]', e
py.commands = ['py', 'python']
py.example = '.py print "Hello world, %s!" % ("James")'


def wa(jenni, input):
    """.wa <input> -- queries WolframAlpha with the given input."""
    if not input.group(2):
        return jenni.reply("No search term.")
    query = input.group(2).encode('utf-8')
    uri = 'https://tumbolia.appspot.com/wa/'
    try:
        answer = web.get(uri + web.urllib.quote(query.replace('+', '%2B')))
    except timeout as e:
        return jenni.say("Request timd out")
    if answer:
        answer = answer.decode("string_escape")
        answer = HTMLParser.HTMLParser().unescape(answer)
        match = re.search('\\\:([0-9A-Fa-f]{4})', answer)
        if match is not None:
            char_code = match.group(1)
            char = unichr(int(char_code, 16))
            answer = answer.replace('\:' + char_code, char)
        waOutputArray = string.split(answer, ";")
        newOutput = list()
        for each in waOutputArray:
            temp = each.replace('\/', '/')
            newOutput.append(temp)
        waOutputArray = newOutput
        if (len(waOutputArray) < 2):
            jenni.say(answer)
        else:
            jenni.say(waOutputArray[0] + " = " + waOutputArray[1])
        waOutputArray = list()
    else:
        jenni.say('Sorry, no result from WolframAlpha.')
wa.commands = ['wa', 'wolfram']
wa.example = '.wa land area of the European Union'

if __name__ == '__main__':
    print __doc__.strip()

#!/usr/bin/env python
"""
url.py - jenni Bitly Module
Copyright 2010-2013, Michael Yanovich (yanovich.net)
Copyright 2010-2013, Kenneth Sham
Licensed under the Eiffel Forum License 2.

More info:
 * jenni: https://github.com/myano/jenni/
 * Phenny: http://inamidst.com/phenny/

This module will record all URLs to bitly via an api key and account.
It also automatically displays the "title" of any URL pasted into the channel.
"""

import json
import re
from htmlentitydefs import name2codepoint
from modules import unicode as uc
import urllib2
import web

# Place a file in your ~/jenni/ folder named, bitly.txt
# and inside this file place your API key followed by a ','
# and then your username. For example, the only line in that
# file should look like this:
# R_d67798xkjc87sdx6x8c7kjc87,myusername

# this variable is to determine when to use bitly. If the URL is more
# than this length, it'll display a bitly URL instead. To disable bit.ly,
# put None even if it's set to None, triggering .bitly command will still work!
BITLY_TRIGGER_LEN_TITLE = 15
BITLY_TRIGGER_LEN_NOTITLE = 70
EXCLUSION_CHAR = '!'
IGNORE = ['git.io']

# do not edit below this line unless you know what you're doing
bitly_loaded = 0
BLOCKED_MODULES = ['title', 'bitly', 'isup', 'py']

try:
    file = open('bitly.txt', 'r')
    key = file.read()
    key = key.split(',')
    bitly_api_key = str(key[0].strip())
    bitly_user = str(key[1].strip())
    file.close()
    bitly_loaded = 1
except:
    print 'ERROR: No bitly.txt found.'

url_finder = re.compile(r'(?u)(%s?(http|https|ftp)(://\S+\.\S+/?\S+?))' %
                        (EXCLUSION_CHAR))
r_entity = re.compile(r'&[A-Za-z0-9#]+;')
INVALID_WEBSITE = 0x01


def noteuri(jenni, input):
    uri = input.group(1).encode('utf-8')
    if not hasattr(jenni.bot, 'last_seen_uri'):
        jenni.bot.last_seen_uri = {}
    jenni.bot.last_seen_uri[input.sender] = uri
noteuri.rule = r'(?u).*(http[s]?://[^<> "\x01]+)[,.]?'
noteuri.priority = 'low'


def find_title(url):
    """
    This finds the title when provided with a string of a URL.
    """
    uri = url

    if not uri and hasattr(self, 'last_seen_uri'):
        uri = self.last_seen_uri.get(origin.sender)

    for item in IGNORE:
        if item in uri:
            return False, 'ignored'

    if not re.search('^((https?)|(ftp))://', uri):
        uri = 'http://' + uri

    if 'twitter.com' in uri:
        uri = uri.replace('#!', '?_escaped_fragment_=')

    uri = uc.decode(uri)

    ## proxy the lookup of the headers through .py
    pyurl = u'https://tumbolia.appspot.com/py/'
    code = 'import simplejson;'
    code += "req=urllib2.Request(u'%s', headers={'Accept':'text/html'});"
    code += "req.add_header('User-Agent','Mozilla/5.0 (Windows NT 6.1;"
    code += "rv:17.0) Gecko/20100101 Firefox/17.0'); u=urllib2.urlopen(req);"
    code += "rtn=dict();"
    code += "rtn['headers'] = u.headers.dict;"
    code += "contents = u.read();"
    code += "con = str();"
    code += r'''exec "try: con=(contents).decode('utf-8')\n'''
    code += '''except: con=(contents).decode('iso-8859-1')";'''
    code += "rtn['read'] = con;"
    code += "rtn['url'] = u.url;"
    code += "rtn['geturl'] = u.geturl();"
    code += r"print simplejson.dumps(rtn)"
    query = code % uri
    try:
        temp = web.quote(query)
        u = web.get(pyurl + temp)
    except Exception, e:
        return False, e

    try:
        useful = json.loads(u)
    except:
        print 'Failed to parse JSON for:', uri, 'because:', u[:300],
        return False, u
    info = useful['headers']
    page = useful['read']

    try:
        mtype = info['content-type']
    except:
        return False, 'mtype failed'
    if not (('/html' in mtype) or ('/xhtml' in mtype)):
        return False, str(mtype)

    content = page
    regex = re.compile('<(/?)title( [^>]+)?>', re.IGNORECASE)
    content = regex.sub(r'<\1title>', content)
    regex = re.compile('[\'"]<title>[\'"]', re.IGNORECASE)
    content = regex.sub('', content)
    start = content.find('<title>')
    if start == -1:
        return False, 'NO <title> found'
    end = content.find('</title>', start)
    if end == -1:
        return False, 'NO </title> found'
    content = content[start + 7:end]
    content = content.strip('\n').rstrip().lstrip()
    title = content

    if len(title) > 200:
        title = title[:200] + '[...]'

    def e(m):
        entity = m.group()
        if entity.startswith('&#x'):
            cp = int(entity[3:-1], 16)
            meep = unichr(cp)
        elif entity.startswith('&#'):
            cp = int(entity[2:-1])
            meep = unichr(cp)
        else:
            char = name2codepoint[entity[1:-1]]
            meep = unichr(char)
        try:
            return uc.decode(meep)
        except:
            return uc.decode(uc.encode(meep))

    title = r_entity.sub(e, title)

    title = title.replace('\n', '')
    title = title.replace('\r', '')

    def remove_spaces(x):
        if '  ' in x:
            x = x.replace('  ', ' ')
            return remove_spaces(x)
        else:
            return x

    title = remove_spaces(title)

    new_title = str()
    for char in title:
        unichar = uc.encode(char)
        if len(list(uc.encode(char))) <= 3:
            new_title += uc.encode(char)
    title = new_title

    title = re.sub(r'(?i)dcc\ssend', '', title)

    if title:
        return True, title
    else:
        return False, 'No Title'


def short(text):
    """
    This function creates a bitly url for each url in the provided string.
    The return type is a list.
    """

    if not bitly_loaded:
        return list()
    if not text:
        return list()
    bitlys = list()
    try:
        a = re.findall(url_finder, text)
        k = len(a)
        i = 0
        while i < k:
            b = uc.decode(a[i][0])
            if not b.startswith('http://bit.ly') and \
                    not b.startswith('http://j.mp/'):
                longer = urllib2.quote(b)
                url = 'http://api.j.mp/v3/shorten?login=%s' % (bitly_user)
                url += '&apiKey=%s&longUrl=%s&format=txt' % (bitly_api_key,
                                                             longer)
                shorter = web.get(url)
                shorter.strip()
                bitlys.append([b, shorter])
            else:
                bitlys.append([b, b])
            i += 1
        return bitlys
    except:
        return


def generateBitLy(jenni, input):
    if not bitly_loaded:
        return
    bitly = short(input)
    idx = 7
    for b in bitly:
        displayBitLy(jenni, b[0], b[1])
generateBitLy.commands = ['bitly']
generateBitLy.priority = 'high'


def displayBitLy(jenni, url, shorten):
    if url is None or shorten is None:
        return
    u = getTLD(url)
    jenni.say('%s  -  %s' % (u, shorten))


def remove_nonprint(text):
    new = str()
    for char in text:
        x = ord(char)
        if x > 32 and x < 126:
            new += char
    return new


def getTLD(url):
    url = url.strip()
    url = remove_nonprint(url)
    idx = 7
    if url.startswith('https://'):
        idx = 8
    elif url.startswith('ftp://'):
        idx = 6
    u = url[idx:]
    f = u.find('/')
    if f == -1:
        u = url
    else:
        u = url[0:idx] + u[0:f]
    return remove_nonprint(u)


def doUseBitLy(title, url):
    BTL = None
    if title:
        BTL = BITLY_TRIGGER_LEN_TITLE
    else:
        BTL = BITLY_TRIGGER_LEN_NOTITLE
    return bitly_loaded and BTL is not None and len(url) > BTL


def get_results(text):
    if not text:
        return list()
    a = re.findall(url_finder, text)
    k = len(a)
    i = 0
    display = list()
    passs = False
    while i < k:
        url = uc.encode(a[i][0])
        url = uc.decode(url)
        url = uc.iriToUri(url)
        url = remove_nonprint(url)
        domain = getTLD(url)
        if '//' in domain:
            domain = domain.split('//')[1]
        if not url.startswith(EXCLUSION_CHAR):
            passs, page_title = find_title(url)
            if bitly_loaded:
                bitly = short(url)
                bitly = bitly[0][1]
            else:
                bitly = url
            display.append([page_title, url, bitly])
        i += 1
    return passs, display


def show_title_auto(jenni, input):
    '''No command - Automatically displays titles for URLs'''
    for each in BLOCKED_MODULES:
        if input.startswith('.%s ' % (each)):
            ## Don't want it to show duplicate titles
            return
    if len(re.findall('\([\d]+\sfiles\sin\s[\d]+\sdirs\)', input)) == 1:
        ## Directory Listing of files
        return
    status, results = get_results(input)

    k = 1
    for r in results:
        returned_title = r[0]
        orig = r[1]
        bitly_link = r[2]

        if k > 3:
            break
        k += 1

        useBitLy = doUseBitLy(returned_title, orig)

        reg_format = '[ %s ] - %s'
        response = str()

        if status:
            if useBitLy:
                response = reg_format % (uc.decode(returned_title), bitly_link)
            else:
                response = reg_format % (returned_title, getTLD(orig))
        elif len(orig) > BITLY_TRIGGER_LEN_NOTITLE:
            response = '(%s) - %s' % (returned_title, bitly_link)

        if response:
            jenni.say(response)
show_title_auto.rule = '(?iu).*(%s?(http|https)(://\S+)).*' % (EXCLUSION_CHAR)
show_title_auto.priority = 'high'


def show_title_demand(jenni, input):
    '''.title http://google.com/ -- forcibly show titles for a given URL'''
    txt = input.group(2)
    if not txt:
        return jenni.reply('Pleaes give me a URL')
    status, results = get_results(input.group(2))

    for r in results:
        returned_title = r[0]
        orig = r[1]
        bitly_link = r[2]

        if returned_title is None:
            continue

        if status:
            response = '[ %s ]' % (returned_title)
        else:
            response = '(%s)' % (returned_title)
        jenni.reply(response)
show_title_demand.commands = ['title']
show_title_demand.priority = 'high'

if __name__ == '__main__':
    print __doc__.strip()

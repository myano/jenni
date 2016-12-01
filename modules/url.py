#!/usr/bin/env python
"""
url.py - jenni Bitly Module
Copyright 2015, Sujeet Akula (sujeet@freeboson.org)
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
from modules import proxy
import time
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
BITLY_TRIGGER_LEN_TITLE = 30
BITLY_TRIGGER_LEN_NOTITLE = 80
EXCLUSION_CHAR = '!'
IGNORE = list()

# do not edit below this line unless you know what you're doing
bitly_loaded = False
BLOCKED_MODULES = ['bitly', 'head', 'host', 'in', 'ip', 'isup', 'longurl', 'py',
                   'short', 'spotify', 'sp', 'st', 'tell', 'title', 'tw',
                   'twitter', 'unbitly', 'untiny', 'fixurl', 'fix_url', 'isgd']

BAD_EXTENSIONS = ('.png', '.jpg', '.jpeg', '.bmp', '.tiff', '.gif', '.pdf',
                  '.doc', '.docx', '.deb', '.rpm', '.exe', '.zip', '.7z', '.gz',
                  '.tar', '.webm', '.mp4', '.mp3', '.avi', '.mpeg', '.mpg',
                  '.ogv', '.ogg', '.java')

simple_channels = list()

try:
    file = open('bitly.txt', 'r')
    key = file.read()
    key = key.split(',')
    bitly_api_key = str(key[0].strip())
    bitly_user = str(key[1].strip())
    file.close()
    bitly_loaded = True
except:
    print 'WARNING: No bitly.txt found.'

try:
    f = open('simple_channels.txt', 'r')
    channels = f.read()
    channels = channels.split(',')
    for channel in channels:
        simple_channels.append(channel.strip())
    f.close()
except:
    print 'WARNING: No simple_channels.txt found'

url_finder = re.compile(r'(?iu)(%s?(http|https|ftp)(://\S+\.?\S+/?\S+?))' %
                        (EXCLUSION_CHAR))
r_entity = re.compile(r'&[A-Za-z0-9#]+;')
INVALID_WEBSITE = 0x01
HTML_ENTITIES = { 'apos': "'" }


def noteuri(jenni, input):
    uri = input.group(1).encode('utf-8')
    if not hasattr(jenni, 'last_seen_uri'):
        jenni.last_seen_uri = {}
    jenni.last_seen_uri[input.sender] = uri
noteuri.rule = r'(?u).*(http[s]?://[^<> "\x01]+)[,.]?'
noteuri.priority = 'low'


def get_page_backup(url):
    req = urllib2.Request(url, headers={'Accept':'*/*'})
    req.add_header('User-Agent', 'Mozilla/5.0 (Windows NT 6.1; rv:24.0) Gecko/20100101 Firefox/24.0')
    u = urllib2.urlopen(req)
    contents = u.read(262144)
    out = dict()
    try:
        con = (contents).decode('utf-8')
    except:
        con = (contents).decode('iso-8859-1')
    out['code'] = u.code
    out['read'] = con
    out['geturl'] = u.geturl()
    out['headers'] = u.headers.dict
    out['url'] = u.url
    return out['code'], out


def find_title(url):
    """
    This finds the title when provided with a string of a URL.
    """

    for item in IGNORE:
        if item in url:
            return False, 'ignored'

    if not re.search('^((https?)|(ftp))://', url):
        url = 'http://' + url

    if '/#!' in url:
        url = url.replace('/#!', '/?_escaped_fragment_=')

    if 'i.imgur' in url:
        a = url.split('.')
        url = a[0][:-1] + '.'.join(a[1:-1])

    if 'zerobin.net' in url:
        return True, 'ZeroBin'

    url = uc.decode(url)

    msg = str()
    k = 0
    status = False

    while not status:
        if 'i.imgur' not in url:
            real_parts = url.split('?')
            if real_parts and real_parts[0].endswith(BAD_EXTENSIONS):
                break

        k += 1
        if k > 3:
            break

        msg = dict()

        try:
            ## 256 kilobytes
            status, msg = proxy.get_more(url, 1024 * 256)
        except:
            try:
                status, msg = get_page_backup(url)
                print "[url] Proxy isn't working!"
            except:
                print '[url] Proxy and "get_page_backup" have both failed!'
                continue

        if type(msg) == type(dict()) and 'code' in msg:
            status = msg['code']
        else:
            continue

        time.sleep(0.5)


    if not status:
        return False, msg

    useful = msg

    info = useful['headers']
    page = useful['read']

    try:
        mtype = info['content-type']
    except:
        print 'failed mtype:', str(info)
        return False, 'mtype failed'
    if not (('/html' in mtype) or ('/xhtml' in mtype)):
        return False, str(mtype)

    content = page


    try:
        from bs4 import BeautifulSoup
        soup = BeautifulSoup(content, 'html.parser')
        title = soup.title.text

    except:
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


    def e(m):
        entity = m.group()
        if entity.startswith('&#x'):
            cp = int(entity[3:-1], 16)
            meep = unichr(cp)
        elif entity.startswith('&#'):
            cp = int(entity[2:-1])
            meep = unichr(cp)
        else:
            entity_stripped = entity[1:-1]
            try:
                char = name2codepoint[entity_stripped]
                meep = unichr(char)
            except:
                if entity_stripped in HTML_ENTITIES:
                    meep = HTML_ENTITIES[entity_stripped]
                else:
                    meep = str()
        try:
            return uc.decode(meep)
        except:
            return uc.decode(uc.encode(meep))

    title = r_entity.sub(e, title)

    title = title.replace('\n', ' ')
    title = title.replace('\r', ' ')
    title = title.replace('\t', ' ')

    def remove_spaces(x):
        if '  ' in x:
            x = x.replace('  ', ' ')
            return remove_spaces(x)
        else:
            return x


    new_title = str()
    for char in title:
        unichar = uc.encode(char)
        if len(list(uc.encode(char))) <= 3:
            new_title += uc.encode(char)
    title = new_title

    title = re.sub(r'(?i)dcc\ssend', '', title)

    title = remove_spaces(title)
    title = (title).strip()

    title += '\x0F'

    if len(title) > 200:
        title = title[:200] + '\x0F[...]'


    if title:
        return True, title
    else:
        return False, 'No Title'

def is_bitly(txt):
    bitly_domains = ['//j.mp', '//bit.ly', '//bitly.com']
    for each in bitly_domains:
        if each in txt:
            return True
    return False


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
            ## make sure that it is not already a bitly shortened link
            if not is_bitly(b):
                longer = urllib2.quote(b)
                url = 'https://api-ssl.bitly.com/v3/shorten?login=%s' % (bitly_user)
                url += '&apiKey=%s&longUrl=%s&format=txt' % (bitly_api_key,
                                                             longer)
                #shorter = proxy.get(url)
                shorter = web.get(url)
                shorter.strip()
                shorter = shorter.replace('j.mp', 'bit.ly')
                bitlys.append([b, shorter])
            else:
                bitlys.append([b, str()])
            i += 1
            return bitlys
    except:
        return
    return bitlys


def generateBitLy(jenni, input):
    url = input.group(2)
    if not url:
        if hasattr(jenni, 'last_seen_uri') and input.sender in jenni.last_seen_uri:
            url = jenni.last_seen_uri[input.sender]
        else:
            return jenni.say('No URL provided')

    bitly = short(url)
    for b in bitly:
        displayBitLy(jenni, b[0], b[1])
generateBitLy.commands = ['bitly']
generateBitLy.priority = 'high'


def displayBitLy(jenni, url, shorten):
    if url is None or shorten is None:
        return
    u = getTLD(url)
    shorten = shorten.replace('http:', 'https:')
    jenni.say('%s  -  %s' % (u, shorten))


def remove_nonprint(text):
    new = str()
    for char in text:
        x = ord(char)
        if x > 32 and x <= 126:
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


def get_results(text, manual=False):
    if not text:
        return False, list()
    a = re.findall(url_finder, text)
    k = len(a)
    i = 0
    display = list()
    passs = False
    channel = str()
    if hasattr(text, 'sender'):
        channel = text.sender
    while i < k:
        url = uc.encode(a[i][0])
        url = uc.decode(url)
        url = uc.iriToUri(url)
        url = remove_nonprint(url)
        domain = getTLD(url)
        if '//' in domain:
            domain = domain.split('//')[1]
        if 'i.imgur.com' in url and url.startswith('http://'):
            url = url.replace('http:', 'https:')

        bitly = url

        if not url.startswith(EXCLUSION_CHAR):
            passs, page_title = find_title(url)
            if not manual:
                if bitly_loaded:
                    if channel and channel not in simple_channels:
                        bitly = short(url)
                        if bitly:
                            bitly = bitly[0][1]
            display.append([page_title, url, bitly, passs])
        else:
            ## has exclusion character
            if manual:
                ## only process excluded URLs if .title is used
                url = url[1:]
                passs, page_title = find_title(url)
                display.append([page_title, url, bitly, passs])
        i += 1

    ## check to make sure at least 1 URL worked correctly
    overall_pass = False
    for x in display:
        if x[-1] == True:
            overall_pass = True

    return overall_pass, display


def show_title_auto(jenni, input):
    '''No command - Automatically displays titles for URLs'''
    for each in BLOCKED_MODULES:
        if input.startswith('.%s ' % (each)):
            ## Don't want it to show duplicate titles
            return

    if hasattr(jenni.config, 'auto_title_disable_chans'):
        disabled_channels = jenni.config.auto_title_disable_chans
        if input.sender in disabled_channels or (input.sender).lower() in disabled_channels:
            return

    if len(re.findall('\([\d]+\sfiles\sin\s[\d]+\sdirs\)', input)) == 1:
        ## Directory Listing of files
        return

    try:
        status, results = get_results(input)
    except Exception, e:
        print '[%s]' % e, input
        return

    k = 1

    output_shorts = str()
    results_len = len(results)

    for r in results:
        ## loop through link, shorten pairs, and titles
        returned_title = r[0]
        orig = r[1]
        bitly_link = r[2]
        link_pass = r[3]


        if orig and bitly_link and bitly_link != orig and ('bit.ly' in bitly_link or 'j.mp' in bitly_link):
            ## if we get back useful data
            ## and we have a bitly link (bitly worked!)
            ## and the shortened link is 'valid'
            ## let's make it 'https' instead of 'http'
            bitly_link = bitly_link.replace('http:', 'https:')

        if returned_title and 'imgur: the most awesome images on the internet' in (returned_title).lower():
            ## because of the i.imgur hack above this is done
            ## to prevent from showing useless titles on image
            ## files
            return

        if k > 3:
            ## more than 3 titles to show from one line of text?
            ## let's just show only the first 3.
            break
        k += 1

        ## deteremine if we should display the bitly link
        useBitLy = doUseBitLy(returned_title, orig)

        reg_format = '[ %s ] - %s'
        special_format = '[ %s ]'
        response = str()

        if status and link_pass:
            if useBitLy and input.sender not in simple_channels and bitly_link:
                response = reg_format % (uc.decode(returned_title), bitly_link)
            else:
                if input.sender in simple_channels:
                    response = special_format % (returned_title)
                else:
                    response = reg_format % (returned_title, getTLD(orig))
        elif len(orig) > BITLY_TRIGGER_LEN_NOTITLE:
            if useBitLy and bitly_link != orig:
                #response = '%s' % (bitly_link)
                output_shorts += bitly_link + ' '
            else:
                ## Fail silently, link can't be bitly'ed and no title was found
                pass

        if response:
            jenni.say(response)

    if output_shorts:
        jenni.say((output_shorts).strip())
show_title_auto.rule = '(?iu).*(%s?(http|https)(://\S+)).*' % (EXCLUSION_CHAR)
show_title_auto.priority = 'high'


def show_title_demand(jenni, input):
    '''.title http://google.com/ -- forcibly show titles for a given URL'''
    uri = input.group(2)

    if uri and 'http' not in uri:
        uri = 'http://' + uri

    if not uri:
        channel = input.sender
        if not hasattr(jenni, 'last_seen_uri'):
            jenni.last_seen_uri = dict()
        if channel in jenni.last_seen_uri:
            uri = jenni.last_seen_uri[channel]
        else:
            return jenni.say('No recent links seen in this channel.')

    status, results = get_results(uri, True)

    for r in results:
        returned_title = r[0]
        orig = r[1]
        bitly_link = r[2]
        link_pass = r[3]

        if returned_title is None:
            jenni.say('No title returned.')
            continue

        if status and link_pass:
            response = '[ %s ]' % (returned_title)
        else:
            response = '(%s)' % (returned_title)
        jenni.say(response)
show_title_demand.commands = ['title']
show_title_demand.priority = 'high'


def collect_links(jenni, input):
    link = input.groups()
    channel = input.sender
    link = link[0]
    if not hasattr(jenni, 'last_seen_uri'):
        jenni.last_seen_uri = dict()
    jenni.last_seen_uri[channel] = link
collect_links.rule = '(?iu).*(%s?(http|https)(://\S+)).*' % (EXCLUSION_CHAR)
collect_links.priority = 'low'

re_meta = re.compile('(?i)content="\S+;\s*?url=(\S+)"\s*?>')


def unbitly(jenni, input):
    '''.longurl <link> -- obtain the final destination URL from a short URL'''
    url = input.group(2)
    if not url:
        if hasattr(jenni, 'last_seen_uri') and input.sender in jenni.last_seen_uri:
            url = jenni.last_seen_uri[input.sender]
        else:
            return jenni.say('No URL provided')
    if not url.startswith(('http://', 'https://')):
        url = 'http://' + url

    status, useful = proxy.get_more(url)
    try:
        new_url = re_meta.findall(useful['read'])
    except:
        return jenni.say(str(useful))

    if new_url:
        new_url = new_url[0]
    else:
        url = url.replace("'", r"\'")
        try:
            status, results = proxy.get_more(url)
            new_url = results['geturl']
        except:
            return jenni.say('Failed to grab URL: %s' % (url))

    channel = input.sender
    if not hasattr(jenni, 'last_seen_uri'):
        jenni.last_seen_uri = dict()
    jenni.last_seen_uri[channel] = new_url

    if new_url.startswith(('http://', 'https://')):
        jenni.say(new_url)
    else:
        jenni.say('Failed to obtain final destination.')
unbitly.commands = ['unbitly', 'untiny', 'longurl', 'st', 'short']
unbitly.priority = 'low'
unbitly.example = '.unbitly http://git.io/6fY4OQ'


def puny(jenni, input):
    '''.puny -- convert to xn-- code for URLs'''
    text = input.group(2)
    if not text:
        return jenni.say('No input provided.')

    if text.startswith('xn--'):
        text = text[4:]
        text_ascii = (text).encode('utf-8')
        try:
            text_unpuny = (text_ascii).decode('punycode')
        except:
            return jenni.say('Stop being a twat.')
        output = (text_unpuny).encode('utf-8')
        output = (output).decode('utf-8')
    else:
        text = (text).encode('utf-8')
        text_utf = (text).decode('utf-8')

        text_puny = (text_utf).encode('punycode')

        output = 'xn--' + text_puny

    return jenni.say(output)
puny.commands = ['puny', 'idn', 'idna']


if __name__ == '__main__':
    print __doc__.strip()

#!/usr/bin/env python
"""
twitter.py - jenni Twitter Module
Copyright 2012-2013, Michael Yanovich (yanovich.net)
Copyright 2012-2013, Sean B. Palmer (inamidst.com)
Licensed under the Eiffel Forum License 2.

More info:
 * jenni: https://github.com/myano/jenni/
 * Phenny: http://inamidst.com/phenny/
"""

from htmlentitydefs import name2codepoint
import re
import time
import urllib
import web

from modules import unicode as uc

r_username = re.compile(r'^[a-zA-Z0-9_]{1,15}$')
r_link = re.compile(r'^https?://twitter.com/\S+$')
r_p = re.compile(r'(?ims)(<p class="js-tweet-text.*?</p>|<p class="ProfileTweet-text.*?</p>)')
r_tag = re.compile(r'(?ims)<[^>]+>')
r_anchor = re.compile(r'(?ims)(<a.*?</a>)')
r_expanded = re.compile(r'(?ims)data-expanded-url=["\'](.*?)["\']')
r_whiteline = re.compile(r'(?ims)[ \t]+[\r\n]+')
r_breaks = re.compile(r'(?ims)[\r\n]+')
r_entity = re.compile(r'&[A-Za-z0-9#]+;')

def entity(*args, **kargs):
    return web.entity(*args, **kargs).encode('utf-8')

def decode(html):
    return web.r_entity.sub(entity, html)

def expand(tweet):
    def replacement(match):
        anchor = match.group(1)
        for link in r_expanded.findall(anchor):
            return link
        return r_tag.sub('', anchor)
    return r_anchor.sub(replacement, tweet)

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


def read_tweet(url):
    bytes = web.get(url)
    shim = '<div class="content clearfix">'
    if shim in bytes:
        bytes = bytes.split(shim, 1).pop()

    for text in r_p.findall(bytes):
        text = expand(text)
        text = r_tag.sub('', text)
        text = text.strip()
        text = r_entity.sub(e, uc.decode(text))
        text = r_whiteline.sub(' ', text)
        text = r_breaks.sub(' ', text)
        return decode(text)
    return "Sorry, couldn't get a tweet from %s" % url

def format(tweet, username):
    return '%s (@%s)' % (tweet, username)

def user_tweet(username):
    tweet = read_tweet('https://twitter.com/' + username + '/with_replies?' + str(time.time()))
    return format(tweet, username)

def id_tweet(tid):
    link = 'https://twitter.com/-/status/' + tid
    error = "Sorry, couldn't get a tweet from %s" % link

    data = web.head_info(link)
    code = data.get('code', 0)
    code = int(code)

    url = str()

    if code == 301:
        url = data.get('info', dict()).get('Location')
    elif code == 200:
        url = data.get('geturl')
    else:
        return error

    if not url:
        return error

    username = url.split('/')[3]
    tweet = read_tweet(url)
    return format(tweet, username)

def twitter(jenni, input):
    arg = input.group(2)

    if not arg:
        if hasattr(jenni, 'last_seen_uri') and input.sender in jenni.last_seen_uri:
            temp = jenni.last_seen_uri[input.sender]
            if '//twitter.com' in temp:
                arg = temp
            else:
                return jenni.say('Last link seen in this channel is not from twitter.com.')
        else:
            return jenni.reply('Give me a link, a username, or a tweet id.')

    arg = arg.strip()
    if isinstance(arg, unicode):
        arg = arg.encode('utf-8')

    output = str()
    if arg.startswith('@'):
        arg = arg[1:]

    if arg.isdigit():
        output = id_tweet(arg)
    elif r_username.match(arg):
        output = user_tweet(arg)
    elif r_link.match(arg):
        username = arg.split('/')[3]
        tweet = read_tweet(arg)
        output = format(tweet, username)
    else:
        output = 'Give me a link, a username, or a tweet id.'

    output = output.replace('pic.twitter.com', 'https://pic.twitter.com')
    jenni.say(output)
twitter.commands = ['tw', 'twitter']
twitter.thread = True

if __name__ == '__main__':
    print __doc__

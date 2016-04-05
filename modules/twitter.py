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
import json
import oauth2 as oauth
import re
import time
import urllib
import urllib2
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

request_token_url = 'https://twitter.com/oauth/request_token'
access_token_url = 'https://twitter.com/oauth/access_token'
authorize_url = 'https://twitter.com/oauth/authorize'


def initialize_keys(jenni, consumer_key='', consumer_secret=''):
    global client
    if not hasattr(jenni.config, 'twitter_consumer_key') or\
           not hasattr(jenni.config, 'twitter_consumer_secret'):
               return False, "Please sign up for Twitter's API and provide the keys in the configuration."
    consumer_key = jenni.config.twitter_consumer_key
    consumer_secret = jenni.config.twitter_consumer_secret

    try:
        consumer = oauth.Consumer(consumer_key, consumer_secret)
        client = oauth.Client(consumer)
    except:
        return False, "Could not initailize Twitter OAuth connection."

    return True, ''


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

def fixURLs(jcont):
    out_text = jcont['text']
    list_of_urls = jcont['entities']['urls']
    for url in list_of_urls:
        #print url['url']
        if url['url'] in out_text:
            out_text = out_text.replace(url['url'], url['expanded_url'])
    if 'extended_entities' in jcont:
        list_of_more_urls = jcont['extended_entities']['media']
        for url in list_of_more_urls:
            if url['url'] in out_text:
                out_text = out_text.replace(url['url'], url['expanded_url'])
    return out_text

def remove_spaces(x):
    if '  ' in x:
        x = x.replace('  ', ' ')
        return remove_spaces(x)
    else:
        return x


def fetchbyID(term):
    global client
    resp, content = client.request('https://api.twitter.com/1.1/statuses/show.json?id=' + urllib2.quote(term), 'GET')
    if resp['status'] != '200':
        return 'Could not reach Twitter API.'
    return content


def fetchbyUserName(term):
    global client
    resp, content = client.request("https://api.twitter.com/1.1/statuses/user_timeline.json?count=1&screen_name=" + term, "GET")
    if resp['status'] == '401':  # tweets are private
        return '{0}\'s tweets are not public.'.format(term)
    if resp['status'] != '200':
        return 'Could not reach Twitter API.'
    try:
        json_content = json.loads(content)
    except:
        return 'Could not make sense of data from Twitter API.'

    #return format_tweet(json_content[0])
    return json.dumps(json_content[0])


def format_tweet(content):
    txt = fixURLs(content)
    #txt = uc.encode(txt)
    txt = expand(txt)
    txt = txt.strip()
    #txt = uc.decode(txt)
    #txt = uc.encode(txt)
    #txt = uc.decode(txt)
    txt = r_entity.sub(e, txt)
    txt = r_whiteline.sub(' ', txt)
    txt = r_breaks.sub(' ', txt)
    txt = decode(txt)
    txt = remove_spaces(txt)
    txt = txt.replace('http://twitter.c', 'https://twitter.c')

    posted = content['created_at']
    fav_count = content['favorite_count']
    rt_count = content['retweet_count']
    name = content['user']['screen_name']

    return u'{1} | By: @{0}, Date: {2}, RT#: {3}, Favs: {4}'.format(name, txt, posted, rt_count, fav_count)


def call_twitter(query):
    ans = None

    params = query.strip().split()

    if len(params) == 1:
        # Only one parameter. By default a username.
        # Also allow a twitter URL or an id number
        if query.startswith('http'):
            ## example: https://twitter.com/username/status/46611258765606912
            m = re.match(r'https?://(?:www\.)?twitter\.com/\w*/status/(\d+)', query)
            if not m:
                return 'Could not parse twitter url.'
            return fetchbyID(m.group(1))

        if query.isdigit():
            return fetchbyID(query)
        else:
            return fetchbyUserName(query)

    elif len(params) == 2:
        # two params means user and status id, which is the same as
        # just status id
        return fetchbyID(params[1])

    else:
        return '??'


def twitter(jenni, input):
    status, response = initialize_keys(jenni)
    if not status:
        return jenni.say(response)

    arg = input.group(2)

    if not arg:
        if hasattr(jenni, 'last_seen_uri') and input.sender in jenni.bot.last_seen_uri:
            temp = jenni.bot.last_seen_uri[input.sender]
            if '//twitter.com' in temp:
                arg = temp
            else:
                return jenni.say('Last link seen in this channel is not from twitter.com.')
        else:
            return jenni.reply('Give me a link, a username, or a tweet id.')

    page = call_twitter(arg)

    try:
        json_page = json.loads(page)
    except:
        return jenni.say(str(page))
    if 'user' in json_page and 'protected' in json_page['user'] and json_page['user']['protected']:
        return jenni.say('This user has their tweets "protected."')

    if 'retweeted_status' in json_page:
        out = u'RT: '
        out += format_tweet(json_page['retweeted_status'])
    else:
        out = format_tweet(json_page)
    return jenni.say(out)

twitter.commands = ['tw', 'twitter']
twitter.thread = True

if __name__ == '__main__':
    print __doc__

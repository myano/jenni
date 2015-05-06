#!/usr/bin/env python
# vim: set fileencoding=UTF-8 :
'''
youtube.py - Youtube Module Improved

Copyright 2015, Josh Begleiter (kanedasan@gmail.com)
Copyright 2014, Sujeet Akula (sujeet@freeboson.org)
Copyright 2012, Dimitri Molenaars, Tyrope.nl.
Copyright 2012-2013, Elad Alfassa, <elad@fedoraproject.org>
Copyright 2012, Edward Powell, embolalia.net

More info:
 * jenni-misc: https://github.com/freeboson/jenni-misc/
 * jenni: https://github.com/myano/jenni/
 * Phenny: http://inamidst.com/phenny/
'''

import json
import re
import traceback
import re, urllib, gzip, StringIO
import web
from HTMLParser import HTMLParser
from modules import proxy

BASE_URL = "https://gdata.youtube.com/feeds/api"

def colorize(text):
  return '\x02\x0306' + text + '\x03\x02'

def ytsearch(jenni, search_term):
    t = urllib.quote_plus(search_term)
    uri = "{0}/videos?q={1}&start-index=1&max-results=10&v=2&alt=json".format(BASE_URL, t)
    bytes = proxy.get(uri)
    result = json.loads(bytes)

    video_entry = result['feed']['entry']
    num_results = result['feed']['openSearch$totalResults']['$t']

    return_text = "YouTube returned {0} results: ".format(num_results)

    entry_text = []

    for entry in video_entry:
        title = entry['title']['$t'].encode('utf8')
        if len(title) > 50:
            title = title[:50] + ' ...'
        title = colorize(title)

        link = None

        for link_hash in entry['link']:
            if link_hash['type'] == "text/html":
                link = link_hash['href'].encode('utf8').\
                    replace('&feature=youtube_gdata','').\
                    replace('https://www.youtube.com', 'https://youtu.be/')
                break

        authors = []

        for author_hash in entry['author']:
            authors.append(author_hash['name']['$t'])

        author = ', '.join(authors).encode('utf8')

        entry_text.append("{0} by {1} ({2})".format(title, author, link))

    all_entries = ""
    if int(num_results) > 0:
      all_entries = ', '.join(entry_text[1:])

    jenni.say(return_text + all_entries)

def youtube_search(jenni, input):
    origterm = input.groups()[1]
    if not origterm:
        return jenni.say('Perhaps you meant ".youtube_search pugs"?')
    origterm = origterm.encode('utf-8')
    origterm = origterm.strip()

    error = None

    try:
        ytsearch(jenni, origterm)
    except IOError:
        error = "An error occurred connecting to YouTube"
        traceback.print_exc()
    except Exception as e:
        error = "An unknown error occurred: " + str(e)
        traceback.print_exc()

    if error is not None:
        jenni.say(error)

youtube_search.commands = ['youtube_search', 'yt_search']
youtube_search.priority = 'high'
youtube_search.rate = 10

def ytinfo(jenni, vid_id):
    t = urllib.quote_plus(vid_id)
    uri = "{0}/videos/{1}?v=2&alt=json".format(BASE_URL, t)

    bytes = proxy.get(uri)
    result = json.loads(bytes)

    if 'feed' in result:
        video_entry = result['feed']['entry'][0]
    else:
        video_entry = result['entry']

    title = video_entry['title']['$t'].encode('utf8')
    if len(title) > 50:
        title = title[:50] + ' ...'
    title = colorize(title)

    link = None

    for link_hash in video_entry['link']:
        if link_hash['type'] == "text/html":
            link = link_hash['href'].encode('utf8').\
                       replace('&feature=youtube_gdata','').\
                       replace('https://www.youtube.com', 'https://youtu.be/')
            break

    authors = []

    for author_hash in video_entry['author']:
        authors.append(author_hash['name']['$t'])

    author = ', '.join(authors).encode('utf8')
    description = video_entry["media$group"]["media$description"]["$t"].encode('utf8')

    if len(description) > 75:
        description = description[:75] + ' ...'

    duration = video_entry["media$group"]["media$content"][0]["duration"]
    favorites = video_entry["yt$statistics"]["favoriteCount"]
    views = video_entry["yt$statistics"]["viewCount"]

    entry_text = "{0} by {1} ({2}). Description: {3}; Duration: {4} seconds; Favorites: {5}; Views: {6}".format(title, author, link, description, duration, favorites, views)

    jenni.say(entry_text)

def youtube_info(jenni, input):
    origterm = input.groups()[1]
    if not origterm:
        return jenni.say('Perhaps you meant ".youtube_info pzPxhaYQQK8"?')
    origterm = origterm.encode('utf-8')
    origterm = origterm.strip()

    error = None

    try:
        ytinfo(jenni, origterm)
    except IOError:
        error = "An error occurred connecting to YouTube"
        traceback.print_exc()
    except Exception as e:
        error = "An unknown error occurred: " + str(e)
        traceback.print_exc()

    if error is not None:
        jenni.say(error)

youtube_info.commands = ['youtube_info', 'yt_info']
youtube_info.priority = 'high'
youtube_info.rate = 10


def remove_spaces(x):
    if '  ' in x:
        x = x.replace('  ', ' ')
        return remove_spaces(x)
    else:
        return x

def process_title(inc):
    outgoing = remove_spaces(inc)
    out = '\x02\x0306' + outgoing + '\x03\x02'
    return out


def title(bot, match):
    """
    Get information about the latest video uploaded by the channel provided.
    """
    if match is None:
        return

    uri = BASE_URL + '/videos/' + match.group(2) + '?v=2&alt=json'

    video_info = ytget(bot, None, uri)
    if video_info is 'err':
        return

    #combine variables and print
    message = '[YouTube] Title: ' + process_title(video_info['title']) + \
              ' | Uploader: ' + video_info['uploader'] + \
              ' | Uploaded: ' + video_info['uploaded'] + \
              ' | Duration: ' + video_info['length'] + \
              ' | Views: ' + video_info['views'] + \
              ' | Comments: ' + video_info['comments'] + \
              ' | Likes: ' + video_info['likes'] + \
              ' | Dislikes: ' + video_info['dislikes'] + \
              ' | Link: ' + video_info['link']

    bot.say(HTMLParser().unescape(message))

    return True


def ytget(bot, trigger, uri):
    #try:
    #bytes = web.get(uri)
    bytes = proxy.get(uri)
    result = json.loads(bytes)
    if 'feed' in result:
        video_entry = result['feed']['entry'][0]
    else:
        video_entry = result['entry']
    #except:
        #bot.say('Something went wrong when accessing the YouTube API.')
        #return 'err'
    vid_info = {}
    try:
        # The ID format is tag:youtube.com,2008:video:RYlCVwxoL_g
        # So we need to split by : and take the last item
        vid_id = video_entry['id']['$t'].split(':')
        vid_id = vid_id[len(vid_id) - 1]  # last item is the actual ID
        vid_info['link'] = 'https://youtu.be/' + vid_id
    except KeyError:
        vid_info['link'] = 'N/A'

    try:
        vid_info['title'] = video_entry['title']['$t']
    except KeyError:
        vid_info['title'] = 'N/A'

    #get youtube channel
    try:
        vid_info['uploader'] = video_entry['author'][0]['name']['$t']
    except KeyError:
        vid_info['uploader'] = 'N/A'

    #get upload time in format: yyyy-MM-ddThh:mm:ss.sssZ
    try:
        upraw = video_entry['published']['$t']
        vid_info['uploaded'] = '%s/%s/%s, %s:%s' % (upraw[0:4], upraw[5:7],
                                                  upraw[8:10], upraw[11:13],
                                                  upraw[14:16])
    except KeyError:
        vid_info['uploaded'] = 'N/A'

    #get duration in seconds
    try:
        duration = int(video_entry['media$group']['yt$duration']['seconds'])
        #Detect liveshow + parse duration into proper time format.
        if duration < 1:
            vid_info['length'] = 'LIVE'
        else:
            hours = duration / (60 * 60)
            minutes = duration / 60 - (hours * 60)
            seconds = duration % 60
            vid_info['length'] = ''
            if hours:
                vid_info['length'] = str(hours) + 'hours'
                if minutes or seconds:
                    vid_info['length'] = vid_info['length'] + ' '
            if minutes:
                vid_info['length'] = vid_info['length'] + str(minutes) + 'mins'
                if seconds:
                    vid_info['length'] = vid_info['length'] + ' '
            if seconds:
                vid_info['length'] = vid_info['length'] + str(seconds) + 'secs'
    except KeyError:
        vid_info['length'] = 'N/A'

    #get views
    try:
        views = video_entry['yt$statistics']['viewCount']
        vid_info['views'] = str('{0:20,d}'.format(int(views))).lstrip(' ')
    except KeyError:
        vid_info['views'] = 'N/A'

    #get comment count
    try:
        comments = video_entry['gd$comments']['gd$feedLink']['countHint']
        vid_info['comments'] = str('{0:20,d}'.format(int(comments))).lstrip(' ')
    except KeyError:
        vid_info['comments'] = 'N/A'

    #get likes & dislikes
    try:
        likes = video_entry['yt$rating']['numLikes']
        vid_info['likes'] = str('{0:20,d}'.format(int(likes))).lstrip(' ')
    except KeyError:
        vid_info['likes'] = 'N/A'
    try:
        dislikes = video_entry['yt$rating']['numDislikes']
        vid_info['dislikes'] = str('{0:20,d}'.format(int(dislikes))).lstrip(' ')
    except KeyError:
        vid_info['dislikes'] = 'N/A'
    return vid_info


def yt_title(bot, trigger):
    uri = trigger.group(2)
    yt_catch = re.compile('http[s]*:\/\/[w\.]*(youtube.com/watch\S*v=|youtu.be/)([\w-]+)')
    yt_match = yt_catch.match(trigger.group(2))
    title(bot, yt_match)
yt_title.commands = ['ytitle']


if __name__ == '__main__':
    print __doc__.strip()

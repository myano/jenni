#!/usr/bin/env python
# vim: set fileencoding=UTF-8 :
'''
youtube.py - Youtube Module Improved v3

Copyright 2015, David Jarrett (jarada.co.uk)
Copyright 2015, Josh Begleiter (kanedasan@gmail.com)
Copyright 2015, Michael Yanovich (yanovich.net)
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

BASE_URL = "https://www.googleapis.com/youtube/v3/"


def colorize(text):
    return '\x02\x0306' + text + '\x03\x02'


def ytsearch(jenni, trigger):
    """Search YouTube"""
    #modified from ytinfo: Copyright 2010-2011, Michael Yanovich, yanovich.net, Kenneth Sham.
    if not hasattr(jenni.config, 'google_dev_apikey'):
        return jenni.say('Please sign up for a Google Developer API key to use this function.')
    key = jenni.config.google_dev_apikey

    query = trigger.group(2).encode('utf-8').strip()
    uri = BASE_URL + "search?part=snippet&type=video&q=" + query + "&key=" + key
    result = json.loads(web.get(uri))

    num_results = result['pageInfo']['totalResults']
    return_text = "YouTube returned {0} results: ".format(num_results)

    entry_text = []
    for item in result['items']:
        try:
            title = item['snippet']['title']
            title = title.encode('utf8')
        except KeyError:
            title = "N/A"
        if len(title) > 50:
            title = title[:50] + ' ...'
        title = colorize(title)

        try:
            author = item['snippet']['channelTitle']
            author = author.encode('utf8')
        except KeyError:
            author = 'N/A'

        link = 'https://youtu.be/' + item['id']['videoId']
        link = link.encode('utf8')

        entry_text.append("{0} by {1} ({2})".format(title, author, link))

    all_entries = ""
    if int(num_results) > 0:
      all_entries = ', '.join(entry_text[1:])

    jenni.say(return_text + all_entries)


def youtube_search(jenni, input):
    origterm = input.groups()[1]
    if not origterm:
        return jenni.say('Perhaps you meant ".yt pugs"?')

    error = None

    try:
        ytsearch(jenni, input)
    except IOError:
        error = "An error occurred connecting to YouTube"
        traceback.print_exc()
    except Exception as e:
        error = "An unknown error occurred: " + str(e)
        traceback.print_exc()

    if error is not None:
        jenni.say(error)
youtube_search.commands = ['yt', 'youtube', 'youtube_search', 'yt_search']
youtube_search.priority = 'high'
youtube_search.rate = 10


def ytinfo(jenni, input):
    video_entry = ytget(jenni, input)

    title = video_entry['title'].encode('utf8')
    if len(title) > 50:
        title = title[:50] + ' ...'
    title = colorize(title)

    link = video_entry['link'].encode('utf8')
    author = video_entry['uploader'].encode('utf8')
    description = video_entry["description"].encode('utf8')

    if len(description) > 75:
        description = description[:75] + ' ...'

    duration = video_entry["length"]
    favorites = video_entry["favourites"]
    views = video_entry["views"]

    entry_text = "{0} by {1} ({2}). Description: {3}; Duration: {4}; Favorites: {5}; Views: {6}".format(title, author, link, description, duration, favorites, views)

    jenni.say(entry_text)


def youtube_info(jenni, input):
    origterm = input.groups()[1]
    if not origterm:
        return jenni.say('Perhaps you meant ".youtube_info pzPxhaYQQK8"?')

    error = None

    try:
        ytinfo(jenni, input)
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


def title(jenni, match):
    """
    Get information about the latest video uploaded by the channel provided.
    """
    if not hasattr(jenni.config, 'google_dev_apikey'):
        return
    if match is None:
        return

    video_info = ytget(jenni, match)
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

    jenni.say(HTMLParser().unescape(message))

    return True


def ytget(jenni, trigger):
    if not hasattr(jenni.config, 'google_dev_apikey'):
        return 'err'

    key = jenni.config.google_dev_apikey

    try:
        vid_id = trigger.group(2)
        uri = BASE_URL + "videos?part=snippet,contentDetails,statistics&id=" + vid_id + "&key=" + key
        bytes = web.get(uri)
        result = json.loads(bytes)
        video_entry = result['items'][0]
    except IndexError:
        jenni.say('Video not found through the YouTube API.')
        return 'err'
    except Exception:
        jenni.say('Something went wrong when accessing the YouTube API.')
        traceback.print_exc()
        return 'err'

    vid_info = {}
    vid_info['link'] = 'https://youtu.be/' + vid_id

    try:
        vid_info['title'] = video_entry['snippet']['title']
    except KeyError:
        vid_info['title'] = 'N/A'

    #get youtube channel
    try:
        vid_info['uploader'] = video_entry['snippet']['channelTitle']
    except KeyError:
        vid_info['uploader'] = 'N/A'

    #get upload time in format: yyyy-MM-ddThh:mm:ss.sssZ
    try:
        upraw = video_entry['snippet']['publishedAt']
        vid_info['uploaded'] = '%s/%s/%s, %s:%s' % (upraw[0:4], upraw[5:7],
                                                  upraw[8:10], upraw[11:13],
                                                  upraw[14:16])
    except KeyError:
        vid_info['uploaded'] = 'N/A'

    #get duration in seconds (contentDetails)
    try:
        if video_entry["snippet"]["liveBroadcastContent"] == "live":
            vid_info['length'] = 'LIVE'
        elif video_entry["snippet"]["liveBroadcastContent"] == "upcoming":
            vid_info['length'] = 'UPCOMING'
        else:
            duration = video_entry["contentDetails"]["duration"]
            # Now replace
            duration = duration.replace("P", "")
            duration = duration.replace("D", "days ")
            duration = duration.replace("T", "")
            duration = duration.replace("H", "hours ")
            duration = duration.replace("M", "mins ")
            duration = duration.replace("S", "secs")
            vid_info['length'] = duration
    except KeyError:
        vid_info['length'] = 'N/A'

    #get views (statistics)
    try:
        views = video_entry['statistics']['viewCount']
        vid_info['views'] = str('{0:20,d}'.format(int(views))).lstrip(' ')
    except KeyError:
        vid_info['views'] = 'N/A'

    #get comment count (statistics)
    try:
        comments = video_entry['statistics']['commentCount']
        vid_info['comments'] = str('{0:20,d}'.format(int(comments))).lstrip(' ')
    except KeyError:
        vid_info['comments'] = 'N/A'

    #get favourites (statistics)
    try:
        favourites = video_entry['statistics']['favoriteCount']
        vid_info['favourites'] = str('{0:20,d}'.format(int(favourites))).lstrip(' ')
    except KeyError:
        vid_info['favourites'] = 'N/A'

    #get likes & dislikes (statistics)
    try:
        likes = video_entry['statistics']['likeCount']
        vid_info['likes'] = str('{0:20,d}'.format(int(likes))).lstrip(' ')
    except KeyError:
        vid_info['likes'] = 'N/A'
    try:
        dislikes = video_entry['statistics']['dislikeCount']
        vid_info['dislikes'] = str('{0:20,d}'.format(int(dislikes))).lstrip(' ')
    except KeyError:
        vid_info['dislikes'] = 'N/A'

    #get video description (snippet)
    try:
        vid_info['description'] = video_entry['snippet']['description']
    except KeyError:
        vid_info['description'] = 'N/A'
    return vid_info


def yt_title(jenni, trigger):
    yt_catch = re.compile('http[s]*:\/\/[w\.]*(youtube.com/watch\S*v=|youtu.be/)([\w-]+)')
    yt_match = yt_catch.match(trigger.group(2))
    title(jenni, yt_match)
yt_title.commands = ['ytitle']


if __name__ == '__main__':
    print __doc__.strip()

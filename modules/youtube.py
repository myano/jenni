#!/usr/bin/env python
'''
youtube.py - Youtube Module

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
from HTMLParser import HTMLParser
import re, urllib, gzip, StringIO
import web


def remove_spaces(x):
    if '  ' in x:
        x = x.replace('  ', ' ')
        return remove_spaces(x)
    else:
        return x


def title(bot, match):
    """
    Get information about the latest video uploaded by the channel provided.
    """
    if match is None:
        return

    uri = 'https://gdata.youtube.com/feeds/api/videos/' + match.group(2) + '?v=2&alt=json'

    video_info = ytget(bot, None, uri)
    if video_info is 'err':
        return

    #combine variables and print
    message = '[YouTube] Title: ' + remove_spaces(video_info['title']) + \
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
    try:
        bytes = web.get(uri)
        result = json.loads(bytes)
        if 'feed' in result:
            video_entry = result['feed']['entry'][0]
        else:
            video_entry = result['entry']
    except:
        bot.say('Something went wrong when accessing the YouTube API.')
        return 'err'
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


def ytsearch(bot, trigger):
    """Search YouTube"""
    #modified from ytinfo: Copyright 2010-2011, Michael Yanovich, yanovich.net, Kenneth Sham.
    if not trigger.group(2):
        return jenni.say('Please provide me some input for YouTube.')
    uri = 'https://gdata.youtube.com/feeds/api/videos?v=2&alt=json&max-results=1&q=' + trigger.group(2).encode('utf-8')
    uri = uri.replace(' ', '+')
    video_info = ytget(bot, trigger, uri)

    if video_info is 'err':
        return bot.reply("Sorry, I couldn't find the video you are looking for.")

    if video_info['link'] == 'N/A':
        return bot.reply("Sorry, I couldn't find the video you are looking for.")

    message = '[YouTube] Title: ' + video_info['title'] + \
              ' | Uploader: ' + video_info['uploader'] + \
              ' | Uploaded: ' + video_info['uploaded'] + \
              ' | Duration: ' + video_info['length'] + \
              ' | Views: ' + video_info['views'] + \
              ' | Comments: ' + video_info['comments'] + \
              ' | Likes: ' + video_info['likes'] + \
              ' | Dislikes: ' + video_info['dislikes'] + \
              ' | Link: ' + video_info['link']

    bot.say(HTMLParser().unescape(message))

ytsearch.commands = ['yt', 'youtube']
ytsearch.priority = 'high'

def ytlast(bot, trigger):
    if not trigger.group(2):
        return jenni.say('Pleae provide some input for YouTube.')
    uri = 'https://gdata.youtube.com/feeds/api/users/' + trigger.group(2).encode('utf-8') + '/uploads?max-results=1&alt=json&v=2'
    video_info = ytget(bot, trigger, uri)

    if video_info is 'err':
        return

    message = ('[Latest Video] Title: ' + remove_spaces(video_info['title']) +
              ' | Duration: ' + video_info['length'] +
              ' | Uploaded: ' + video_info['uploaded'] +
              ' | Views: ' + video_info['views'] +
              ' | Likes: ' + video_info['likes'] +
              ' | Dislikes: ' + video_info['dislikes'] +
              ' | Link: ' + video_info['link'])

    bot.say(HTMLParser().unescape(message))
ytlast.commands = ['ytlast', 'ytnew', 'ytlatest']
ytlast.priority = 'high'

if __name__ == '__main__':
    print __doc__.strip()


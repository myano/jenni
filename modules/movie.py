# -*- coding: utf8 -*-
'''
movie.py - jenni Movie Information Module
Copyright 2014, Michael Yanovich, yanovich.net
Copyright 2012, Elad Alfassa, <elad@fedoraproject.org>
Licensed under the Eiffel Forum License 2.

This module relies on omdbapi.com

More info:
 * jenni: https://github.com/myano/jenni/
 * Phenny: http://inamidst.com/phenny/
'''

import json
import urllib2
import re

API_BASE_URL = 'http://www.omdbapi.com/'


def prep_title(txt):
    txt = txt.replace(' ', '+')
    txt = (txt).encode('utf-8')
    txt = urllib2.quote(txt)
    return txt


def movie(jenni, input):
    '''.imdb movie/show title -- displays information about a production'''

    if not input.group(2):
        return jenni.say('Please enter a movie or TV show title. '
                         'Year is optional.')

    word = input.group(2).rstrip()
    matchObj = re.match(r'([\w\s]*)\s?,\s?(\d{4})', word, re.M | re.I)

    if matchObj:
        title = matchObj.group(1)
        year = matchObj.group(2)
        title = prep_title(title)
        uri = API_BASE_URL + '?t=%s&y=%s&plot=short&r=json' % (title, year)
    else:
        title = word
        title = prep_title(title)
        uri = API_BASE_URL + '?t=%s&plot=short&r=json' % (title)

    try:
        page = urllib2.urlopen(uri).read()
    except:
        return jenni.say('[MOVIE] Connection to API did not succeed.')

    try:
        data = json.loads(page)
    except:
        return jenni.say("[MOVIE] Couldn't make sense of information from API")
    message = '[MOVIE] '

    if data['Response'] == 'False':
        if 'Error' in data:
            message += data['Error']
        else:
            message += 'Got an error from imdbapi'
    else:
        temp = 'Title: %s | Released: %s | Plot: %s '
        temp += '| IMDB Link: http://imdb.com/title/%s/'
        message += temp % (data['Title'], data['Released'], data['Plot'],
                           data['imdbID'])

    jenni.say(message)
movie.commands = ['movie', 'imdb', 'show', 'tv']
movie.example = '.movie Movie Title, 2015'

if __name__ == '__main__':
    print __doc__.strip()

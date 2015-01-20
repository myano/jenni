# -*- coding: utf8 -*-
"""
movie.py - jenni Movie Information Module
Copyright 2012, Elad Alfassa, <elad@fedoraproject.org>
Licensed under the Eiffel Forum License 2.

This module relies on omdbapi.com

More info:
 * jenni: https://github.com/myano/jenni/
 * Phenny: http://inamidst.com/phenny/
"""

import json
import urllib
import urllib2
import re


def movie(jenni, input):
    """.imdb movie/show title -- displays information about a production"""

    if not input.group(2):
        return
    word = input.group(2).rstrip()
    matchObj = re.match( r'([\w\s]*)\s?,\s?(\d{4})', word, re.M|re.I)
    if matchObj:
        title = matchObj.group(1)
        year = matchObj.group(2) 
        title = title.replace(" ", "+")
        uri = "http://www.omdbapi.com/?t=" + title
        uri += "&y="+year+"&plot=short&r=json"
    else:
        title = word
        title = title.replace(" ", "+")
        uri = "http://www.omdbapi.com/?t=" + title +"&plot=short&r=json"


    uri = uri.encode('utf-8')
    page = urllib2.urlopen(uri).read()

    data = json.loads(page)

    if data['Response'] == 'False':
        if 'Error' in data:
            message = '[MOVIE] %s' % data['Error']
        else:
            jenni.debug('movie',
                        'Got an error from the imdb api,\
                                search phrase was %s' %
                        word, 'warning')
            jenni.debug('movie', str(data), 'warning')
            message = '[MOVIE] Got an error from imdbapi'
    else:
        message = '[MOVIE] Title: ' + data['Title'] + \
                  ' | Released: ' + data['Released'] + \
                  ' | Plot: ' + data['Plot'] + \
                  ' | IMDB Link: http://imdb.com/title/' + data['imdbID']
    jenni.say(message)
movie.commands = ['movie', 'imdb']
movie.example = '.movie Movie Title, 2015'

if __name__ == '__main__':
    print __doc__.strip()

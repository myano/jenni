# -*- coding: utf8 -*-
"""
imdb.py - jenni Movie Information Module
Copyright 2012, Elad Alfassa, <elad@fedoraproject.org>
Licensed under the Eiffel Forum License 2.

This module relies on imdbapi.com

More info:
 * jenni: https://github.com/myano/jenni/
 * Phenny: http://inamidst.com/phenny/
"""

import json
import urllib2
import web


def movie(jenni, input):
    """.imdb movie/show title -- displays information about a production"""

    if not input.group(2):
        return
    word = input.group(2).rstrip()
    word = word.replace(" ", "+")
    uri = "http://www.imdbapi.com/?t=" + word

    uri = uri.encode('utf-8')
    page = web.get(uri)
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
                  ' | Year: ' + data['Year'] + \
                  ' | Rating: ' + data['imdbRating'] + \
                  ' | Genre: ' + data['Genre'] + \
                  ' | IMDB Link: http://imdb.com/title/' + data['imdbID']
    jenni.say(message)
movie.commands = ['movie', 'imdb']
movie.example = '.movie Movie Title'

if __name__ == '__main__':
    print __doc__.strip()

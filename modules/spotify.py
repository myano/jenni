#!/usr/bin/python
"""
spotify.py - An api interface for spotify lookups
Copyright 2015 Micheal Harker <micheal@michealharker.com>
Copyright 2012 Patrick Andrew <missionsix@gmail.com>

Licensed under the Eiffel Forum License, version 2

1. Permission is hereby granted to use, copy, modify and/or
   distribute this package, provided that:
      * copyright notices are retained unchanged,
      * any distribution of this package, whether modified or not,
        includes this license text.
2. Permission is hereby also granted to distribute binary programs
   which depend on this package. If the binary program depends on a
   modified version of this package, you are encouraged to publicly
   release the modified version of this package.

THIS PACKAGE IS PROVIDED "AS IS" AND WITHOUT WARRANTY. ANY EXPRESS OR
IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
DISCLAIMED. IN NO EVENT SHALL THE AUTHORS BE LIABLE TO ANY PARTY FOR ANY
DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
DAMAGES ARISING IN ANY WAY OUT OF THE USE OF THIS PACKAGE.
"""

import httplib
import json
import sys

from datetime import timedelta


class NotModifiedError(Exception):
    def __init__(self):
        super(NotModifiedError, self).__init__(
            "The data hasn't changed since your last request.")


class ForbiddenError(Exception):
    def __init__(self):
        super(ForbiddenError, self).__init__(
            "The rate-limiting has kicked in.  Please try again later.")


class NotFoundException(LookupError):
    def __init__(self):
        super(NotFoundException, self).__init__(
            "Could not find that Spotify URI.")


class BadRequestException(LookupError):
    def __init__(self):
        super(BadRequestException, self).__init__(
            "The request was not understood.")


class InternalServerError(Exception):
    def __init__(self):
        super(InternalServerError, self).__init__(
            "The server encounted an unexpected problem.")


class ServiceUnavailable(Exception):
    def __init__(self):
        super(ServiceUnavailable, self).__init__(
            "The API is temporarily unavailable.")

SpotifyStatusCodes = {
    304: NotModifiedError,
    400: BadRequestException,
    403: ForbiddenError,
    404: NotFoundException,
    500: InternalServerError,
    503: ServiceUnavailable
}

TRACK_MSG = '"{0}{1}{0}" [{0}{2}{0}] by {3} from "{0}{4}{0}", which was released in {0}{5}{0}.'
ALBUM_MSG = '"{0}{1}{0}" by {0}{2}{0}, released in {0}{3}{0} and is available in {0}{4}{0} countries.'
ARTIST_MSG = 'Artist: {0}{1}{0}'


class Spotify:

    base_url = "ws.spotify.com"
    service_url = '/lookup/1/.json'

    def __init__(self):
        self.conn = httplib.HTTPConnection(self.base_url)

    def __del__(self):
        self.conn.close()

    def lookup(self, uri, extras=None):

        lookup_url = "%s?uri=%s" % (self.service_url, uri)
        if extras is not None:
            lookup_url += "&extras=%s" % extras

        self.conn.request("GET", lookup_url)
        resp = self.conn.getresponse()
        if resp.status == 200:
            result = json.loads(resp.read())
            return result
        try:
            raise SpotifyStatusCodes[resp.status]
        except ValueError:
            raise Exception("Unknown response from the Spotify API")


def notify(jenni, recipient, text):
    jenni.write(('NOTICE', recipient), text)


def print_album(jenni, album):
    territories = len(album['availability']['territories'].split(' '))

    message = ALBUM_MSG.format(
        "\x02",
        album['name'],
        album['artist'],
        album['released'],
        len(album['availability']['territories'].split(' '))
    )

    jenni.say(message)


def print_artist(jenni, artist):
    message = ARTIST_MSG.format(
        "\x02",
        artist['name']
    )

    jenni.say(message)


def print_track(jenni, track):
    length = str(timedelta(seconds=track['length']))[2:7]
    if length[0] == '0':
        length = length[1:]

    artist_names = [artist['name'] for artist in track['artists']]
    artists = artist_list(artist_names)

    message = TRACK_MSG.format(
        "\x02",
        track['name'],
        length,
        artists,
        track['album']['name'],
        track['album']['released']
    )

    jenni.say(message)


def query(jenni, input):
    spotify = Spotify()
    result = None
    lookup = input.group(1).lstrip().rstrip()
    try:
        result = spotify.lookup('spotify:%s' % lookup)
    except:
        e = sys.exc_info()[0]
        notify(jenni, input.nick, e)
        return

    formatters = {
        'track': print_track,
        'album': print_album,
        'artist': print_artist
    }

    try:
        type = result['info']['type']
        formatters[type](jenni, result[type])
    except KeyError:
        notify(jenni, input.nick, "Unknown response from API server")


def artist_list(data):
    if (len(data) > 1):
        artists = ""
        for artist in data[:-1]:
            artists += "{0}{1}{0}".format("\x02", artist)
            if artist is not data[-2]:
                artists += ", "
        artists += " and {0}{1}{0}".format("\x02", data[-1])
        return artists
    else:
        return "{0}{1}{0}".format("\x02", data[0])

query.rule = r'.*spotify:(.*)$'
query.priority = 'low'


if __name__ == '__main__':
    print __doc__.strip()

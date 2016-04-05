#!/usr/bin/python

"""
spotify.py - An api interface for spotify lookups
Copyright 2015 - 2016 Micheal Harker <micheal@michealharker.com>
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

import json
import sys
from datetime import timedelta

from modules import proxy


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

TRACK_MSG = '"{0}{1}{0}" [{0}{2}{0}] by {3} from "{0}{4}{0}".'
EXPLICIT_TRACK_MSG = '[{0}E{0}]" {0}{1}{0}" [{0}{2}{0}] by {3} from "{0}{4}{0}".'
ALBUM_MSG = '"{0}{1}{0}" by {2}, released in {0}{3}{0}.'
ARTIST_MSG = 'Artist: {0}{1}{0}'

API_URL = "api.spotify.com"
API_ENDPOINT = "/v1"


def lookup(typ, objid):
    url = "https://%s%s/%ss/%s" % (API_URL, API_ENDPOINT, typ, objid)

    success, response = proxy.get_more(url)

    if not success:
        raise Exception("Unable to connect to proxy: {0}".format(response))

    if response['code'] == 200:
        result = json.loads(response['read'])
        return result

    try:
        raise SpotifyStatusCodes[response['code']]
    except KeyError, ValueError:
        raise Exception("HTTP Error {0}".format(response['code']))


def notify(jenni, recipient, text):
    jenni.write(('NOTICE', recipient), text)


def print_album(jenni, album):
    artist_names = [artist['name'] for artist in album['artists']]
    artists = artist_list(artist_names)

    message = ALBUM_MSG.format(
        "\x02",
        album['name'].encode('utf-8'),
        artists.encode('utf-8'),
        album['release_date'][:4]
    )

    jenni.say(message)


def print_artist(jenni, artist):
    message = ARTIST_MSG.format(
        "\x02",
        artist['name'].encode('utf-8')
    )

    jenni.say(message)


def print_track(jenni, track):
    length = str(timedelta(seconds=(track['duration_ms']/1000)))[2:7]
    if length[0] == '0':
        length = length[1:]

    artist_names = [artist['name'] for artist in track['artists']]
    artists = artist_list(artist_names)

    if track['explicit']:
        message_format = EXPLICIT_TRACK_MSG
    else:
        message_format = TRACK_MSG

    message = message_format.format(
        "\x02",
        track['name'].encode('utf-8'),
        length,
        artists.encode('utf-8'),
        track['album']['name'].encode('utf-8')
    )

    jenni.say(message)


def query(jenni, input):
    typ = (input.group(1) or input.group(3)).lower()  # type of object we wanna lookup
    objid = input.group(2) or input.group(4)  # ID of the object like a track, artist, etc.

    formatters = {
        'track': print_track,
        'album': print_album,
        'artist': print_artist
    }

    if typ not in formatters:
        notify(jenni, input.nick, "Unknown object type: {0}".format(typ))
        return

    try:
        result = lookup(typ, objid)
    except Exception as e:
        notify(jenni, input.nick, str(e))
        return

    try:
        formatters[typ](jenni, result)
    except Exception as e:
        notify(jenni, input.nick, str(e))

query.rule = r'(?i).*\bspotify:(\S+):(\S+)|^\.sp(?:otify)? +https?://open\.spotify\.com/(\S+)/(\S+)$'
query.priority = 'low'


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


if __name__ == '__main__':
    print __doc__.strip()

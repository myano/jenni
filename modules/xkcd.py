#!/usr/bin/env python
'''
xkcd.py - XKCD Module
Copyright 2010-2014 Michael Yanovich (yanovich.net), and Morgan Goose
Partially re-written by Paul Schellin (paulschellin@gmail.com) 2014

Licensed under the Eiffel Forum License 2.

More info:
 * jenni: https://github.com/myano/jenni/
 * Phenny: http://inamidst.com/phenny/
'''

import json
import random
import web
import re
from modules import unicode as uc

'''
Randall Munroe is nice and provides a simple JSON API for fetching comics.

See this page:
https://xkcd.com/json.html


Can access:
https://xkcd.com/info.0.json
for the current comic, or:
https://xkcd.com/614/info.0.json
for the 614th comic.

Each comic contains the following JSON keys:

{
 "month": "10"
,"num": 1432
, "link": ""
, "year": "2014"
, "news": ""
, "safe_title": "The Sake of Argument"
, "transcript": ""
, "alt": "'It's not actually ... it's a DEVICE for EXPLORING a PLAUSIBLE REALITY that's not the one we're in, to gain a broader understanding about it.' 'oh, like a boat!' '...' 'Just for the sake of argument, we should get a boat! You can invite the Devil, too, if you want.'"
, "img": "http:\/\/imgs.xkcd.com\/comics\/the_sake_of_argument.png"
, "title": "The Sake of Argument"
, "day": "10"
}

'''

random.seed()


def xkcd(jenni, input):
    '''.xkcd - Print all available information about the most recent (or specified) XKCD clip.'''

    def tryToGetJSON (site_url):
        try:
            page = web.get(xkcd_url)
        except:
            return jenni.say('Failed to access xkcd.com: <' + xkcd_url + '>')
        try:
            body = json.loads(page)
        except:
            return jenni.say('Failed to make use of data loaded by xkcd.com: <' + xkcd_url + '>')
        return body


    xkcd_url = 'https://xkcd.com/info.0.json'

    show_random_comic = False

    line = input.group(2)
    if line:
        if line.isdigit():
            xkcd_num = line.lstrip().rstrip()
            xkcd_url = 'https://xkcd.com/' + xkcd_num + '/info.0.json'
        elif any([line.lower() in ['r', 'ran', 'rand', 'random']]):
            show_random_comic = True
        else:
            jenni.say(u'Incorrect argument for .xkcd: ' + line)


    body = tryToGetJSON(xkcd_url)

    if show_random_comic:
        max_int = body['num']
        xkcd_rand_num = random.randint(0, max_int)
        xkcd_url = 'https://xkcd.com/' + str(xkcd_rand_num) + '/info.0.json'
        body = tryToGetJSON(xkcd_url)


    comic_date_str = body['year'] + u'-' + str(body['month']).zfill(2) + u'-' + str(body['day']).zfill(2)
    header_str = u'\x02xkcd #\x02' + str(body['num']) + u' (' + comic_date_str + u') \x02' + body['title'] + u'\x02'
    jenni.say(header_str)

    if body['transcript'].encode('UTF-8'):
        transcript_text = '\x02Transcript:\x02 ' + body['transcript']
        jenni.say(transcript_text)


    alt_text = u'\x02Alt text\x02: ' + body['alt']
    jenni.say(alt_text)

    img_ssl_link = u'[ ' + re.sub(r'http://', 'https://ssl', body['img']) + u' ]'
    jenni.say(img_ssl_link)


xkcd.commands = ['xkcd']
xkcd.example = '.xkcd  (for most recent), .xkcd [comic number]  (for specific comic), or .xkcd [r | ran | rand | random]  (for a random comic)'
xkcd.priority = 'medium'

if __name__ == '__main__':
    print __doc__.strip()

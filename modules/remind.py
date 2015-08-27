#!/usr/bin/env python
"""
remind.py - jenni Reminder Module
Copyright 2011-2013, Michael Yanovich (yanovich.net)
Copyright 2011-2013, Sean B. Palmer (inamidst.com)
Licensed under the Eiffel Forum License 2.

More info:
 * jenni: https://github.com/myano/jenni/
 * Phenny: http://inamidst.com/phenny/
"""

from datetime import datetime, timedelta
import os
import re
import time
import threading

r_command = None

scaling = {
    'years': 365.25 * 24 * 3600,
    'year': 365.25 * 24 * 3600,
    'yrs': 365.25 * 24 * 3600,
    'y': 365.25 * 24 * 3600,

    'months': 29.53059 * 24 * 3600,
    'month': 29.53059 * 24 * 3600,
    'mo': 29.53059 * 24 * 3600,

    'weeks': 7 * 24 * 3600,
    'week': 7 * 24 * 3600,
    'wks': 7 * 24 * 3600,
    'wk': 7 * 24 * 3600,
    'w': 7 * 24 * 3600,

    'days': 24 * 3600,
    'day': 24 * 3600,
    'd': 24 * 3600,

    'hours': 3600,
    'hour': 3600,
    'hrs': 3600,
    'hr': 3600,
    'h': 3600,

    'minutes': 60,
    'minute': 60,
    'mins': 60,
    'min': 60,
    'm': 60,

    'seconds': 1,
    'second': 1,
    'secs': 1,
    'sec': 1,
    's': 1
}

def filename(self):
    name = self.nick + '-' + self.config.host + '.reminders.db'
    return os.path.join(os.path.expanduser('~/.jenni'), name)

def load_database(name):
    data = {}
    if os.path.isfile(name):
        f = open(name, 'rb')
        for line in f:
            unixtime, channel, nick, message = line.split('\t')
            message = message.rstrip('\n')
            t = int(unixtime)
            reminder = (channel, nick, message)
            try: data[t].append(reminder)
            except KeyError: data[t] = [reminder]
        f.close()
    return data

def dump_database(name, data):
    f = open(name, 'wb')
    for unixtime, reminders in data.iteritems():
        for channel, nick, message in reminders:
            f.write('%s\t%s\t%s\t%s\n' % (unixtime, channel, nick, message))
    f.close()

def setup(jenni):
    global r_command

    periods = '|'.join(scaling.keys())
    p_command = r'{}in ([0-9]+(?:\.[0-9]+)?)\s?((?:{})\b)?:?\s?(.*)'.format(
        jenni.config.prefix,
        periods,
    )
    r_command = re.compile(p_command)

    jenni.rfn = filename(jenni)

    # jenni.sending.acquire()
    jenni.rdb = load_database(jenni.rfn)
    # jenni.sending.release()

    def monitor(jenni):
        time.sleep(5)
        while True:
            now = int(time.time())
            unixtimes = [int(key) for key in jenni.rdb]
            oldtimes = [t for t in unixtimes if t <= now]
            if oldtimes:
                for oldtime in oldtimes:
                    for (channel, nick, message) in jenni.rdb[oldtime]:
                        if message:
                            jenni.msg(channel, nick + ': ' + message)
                        else: jenni.msg(channel, nick + '!')
                    del jenni.rdb[oldtime]

                # jenni.sending.acquire()
                dump_database(jenni.rfn, jenni.rdb)
                # jenni.sending.release()
            time.sleep(2.5)

    targs = (jenni,)
    t = threading.Thread(target=monitor, args=targs)
    t.start()

def remind(jenni, input):
    m = r_command.match(input.bytes)
    if not m:
        return jenni.reply("Sorry, didn't understand the input.")
    length, scale, message = m.groups()

    length = float(length)
    factor = scaling.get(scale, 60)
    duration = length * factor

    if duration % 1:
        duration = int(duration) + 1
    else: duration = int(duration)

    t = int(time.time()) + duration
    message += ' | Set on: ' + str(datetime.now().isoformat())
    reminder = (input.sender, input.nick, message)

    try: jenni.rdb[t].append(reminder)
    except KeyError: jenni.rdb[t] = [reminder]

    dump_database(jenni.rfn, jenni.rdb)

    if duration >= 60:
        try:
            w = ''
            if duration >= 3600 * 12:
                w += time.strftime(' on %d %b %Y', time.gmtime(t))
            w += time.strftime(' at %H:%MZ', time.gmtime(t))
            jenni.reply('Okay, will remind%s' % w)
        except:
            jenni.reply('Please enter a more realistic time-frame.')
    else: jenni.reply('Okay, will remind in %s secs' % duration)
remind.commands = ['in']

r_time = re.compile(r'.*([0-9]{2}[:.][0-9]{2}).*')
r_zone = re.compile(r'(?:[\d]{4}-[\d]{2}-[\d]{2})?\s+?(([A-Za-z]+|[+-]\d\d?)).*')
r_date = re.compile(r'([\d]{4})-([\d]{2})-([\d]{2})')

import calendar
from modules import clock

def at(jenni, input):
    '''.at YYYY-MM-DD HH:MM TZ -- remind at a specific time.'''
    ## input can be just a HH:MM TZ if you want the same day

    help_txt = 'Accepted date inputs are: "YYYY-MM-DD HH:MM TZ" and "HH:MM TZ"'

    txt = input.groups(2)
    if not txt:
        return jenni.say(help_txt)

    ## remove the ".at " part
    ## yea, yea, there are better ways at doing this
    ## but LEGACY!
    bytes = input[4:]

    ## look for time matching the pattern:
    ## r'.*([0-9]{2}[:.][0-9]{2}).*'
    ## basically (just a time without a date)
    m = r_time.findall(bytes)

    if not m:
        ## even if a date is specified, if we couldn't find a specific time
        ## we don't know *when* to remind the user
        return jenni.reply("Sorry, I couldn't find the time. " + help_txt)

    ## : are better than .
    ## but we should still accept .
    t = m[0].replace('.', ':')

    ## look for full part
    ## r'(?:[\d]{4}-[\d]{2}-[\d]{2})?\s+?(([A-Za-z]+|[+-]\d\d?)).*'
    m = r_zone.findall(bytes)

    if not m:
        return jenni.reply("Sorry, I couldn't figure out what date you wanted. " + help_txt)

    ## pluck out the [A-Za-z]+|[+-]\d\d?
    z = m[0][0]

    tz = None

    ## check to see if someone used an offset instead of a named timezone
    if z.startswith('+') or z.startswith('-'):
        tz = int(z)

    ## if they didn't use an offset
    if not tz:
        ## let's find an offset!
        if clock.TimeZones.has_key(z):
            tz = clock.TimeZones[z]
        else:
            ## default to UTC
            ## UTC is much better
            tz = 0
            z = 'UTC'

    ## let's look for the specific date
    ## r'([\d]{4})-([\d]{2})-([\d]{2})'
    try_date = r_date.findall(bytes)

    if try_date:
        td = try_date[0]
        dt = datetime(int(td[0]), int(td[1]), int(td[2]), int(t[0:2]), int(t[3:]))
        dt -= timedelta(hours=tz)
        print 'dt:', str(dt)
        time_delta = dt - datetime.now()
        print 'time_delta:', str(time_delta)

        duration = time_delta.total_seconds()
        unix_stamp_event = int(time.mktime(dt.timetuple()))
    else:
        d = time.strftime('%Y-%m-%d', time.gmtime())
        d = time.strptime(('%s %s' % (d, t)).encode('utf-8'), '%Y-%m-%d %H:%M')

        d = int(calendar.timegm(d) - (3600.0 * tz))

        duration = int(d - time.time())
        if duration < 1:
            d = time.strftime('%Y-%m-%d', time.gmtime())
            d = time.strptime(('%s %s' % (d, t)).encode('utf-8'), '%Y-%m-%d %H:%M')
            d = int((calendar.timegm(d) + 86400.0) - (3600.0 * tz))
            duration = int(d - time.time())

        unix_stamp_event = d

    t_duration = 0
    duration = float(duration)
    phrase = str()
    ## make the output remaining time look pretty
    if duration >= (86400.0 * 365 * 2):  # 2 years
        t_years = duration / (86400 * 365)
        t_duration = '%.2f' % (t_years)
        phrase = 'years'
    elif duration >= (86400.0 * 60):  # 2 months
        t_months = duration / (86400.0 * 30)
        t_duration = '%.2f' % (t_months)
        phrase = 'months'
    elif duration >= (86400.0 * 14):  # 2 weeks
        t_weeks = duration / (86400.0 * 7)
        t_duration = '%.2f' % (t_weeks)
        phrase = 'weeks'
    elif duration >= (86400.0 * 2):  # 2 days
        t_days = duration / 86400.0
        t_duration = '%.2f' % (t_days)
        phrase = 'days'
    elif duration >= (3600.0 * 2):  # 2 hours
        t_hours = duration / 3600.0
        t_duration = '%.2f' % (t_hours)
        phrase = 'hours'
    elif duration >= 60.0:
        t_minutes = duration / 60.0
        t_duration = '%.2f' % (t_minutes)
        phrase = 'minutes'
    elif duration >= 0:
        t_duration = '%.2f' % (duration)
        phrase = 'seconds'
    else:
        ## well crap, the duration must be negative!
        return jenni.reply('Sorry, but that occurs in the past! Please select a time in the future.')

    ## who do we need to remind? and where? and what?
    reminder = (input.sender, input.nick, bytes)

    ## store such information
    try: jenni.rdb[unix_stamp_event].append(reminder)
    except KeyError: jenni.rdb[unix_stamp_event] = [reminder]

    ## threading/reminding voodoo
    jenni.sending.acquire()
    dump_database(jenni.rfn, jenni.rdb)
    jenni.sending.release()

    ## communicate to the user!
    jenni.reply('Reminding at %s %s - in %s %s' % (t, z, t_duration, phrase))
at.commands = ['at']

if __name__ == '__main__':
    print __doc__.strip()


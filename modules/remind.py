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

import os, re, time, threading

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

periods = '|'.join(scaling.keys())
p_command = r'\.in ([0-9]+(?:\.[0-9]+)?)\s?((?:%s)\b)?:?\s?(.*)' % periods
r_command = re.compile(p_command)

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

r_time = re.compile(r'^([0-9]{2}[:.][0-9]{2})')
r_zone = re.compile(r'( ?([A-Za-z]+|[+-]\d\d?))')

import calendar
from modules import clock

def at(jenni, input):
    bytes = input[4:]

    m = r_time.match(bytes)
    if not m:
        return jenni.reply("Sorry, didn't understand the time spec.2")
    t = m.group(1).replace('.', ':')
    bytes = bytes[len(t):]

    m = r_zone.match(bytes)
    if not m:
        return jenni.reply("Sorry, didn't understand the zone spec.3")
    z = m.group(2)
    bytes = bytes[len(m.group(1)):].strip().encode("utf-8")

    if z.startswith('+') or z.startswith('-'):
        tz = int(z)

    if clock.TimeZones.has_key(z):
        tz = clock.TimeZones[z]
    else: return jenni.reply("Sorry, didn't understand the time zone.4")

    d = time.strftime("%Y-%m-%d", time.gmtime())
    d = time.strptime(("%s %s" % (d, t)).encode("utf-8"), "%Y-%m-%d %H:%M")

    d = int(calendar.timegm(d) - (3600 * tz))
    duration = int((d - time.time()) / 60)

    if duration < 1:
        return jenni.reply("Sorry, that date is this minute or in the past. And only times in the same day are supported!")

    # jenni.say("%s %s %s" % (t, tz, d))

    reminder = (input.sender, input.nick, bytes)
    # jenni.say(str((d, reminder)))
    try: jenni.rdb[d].append(reminder)
    except KeyError: jenni.rdb[d] = [reminder]

    jenni.sending.acquire()
    dump_database(jenni.rfn, jenni.rdb)
    jenni.sending.release()

    jenni.reply("Reminding at %s %s - in %s minute(s)" % (t, z, duration))
at.commands = ['at']

if __name__ == '__main__':
    print __doc__.strip()


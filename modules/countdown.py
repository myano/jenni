#!/usr/bin/env python
"""
countdown.py - jenni Countdown Module
Copyright 2011-2013, Michael Yanovich (yanovich.net)
Licensed under the Eiffel Forum License 2.

More info:
 * jenni: https://github.com/myano/jenni/
 * Phenny: http://inamidst.com/phenny/
"""

from datetime import datetime, timedelta

bad_format = "Please use correct format: .countdown 2012 12 21 You can also try: '.nye -5'"
## 2036 02 07

def get_output(calculate_date, today, nye):
    #ending = "%s %s-%s-%sT%s00Z"
    verb = str()
    if calculate_date <= today:
        diff = today - calculate_date
        verb = "since"
#        if nye:
#            return get_output(calculate_date + timedelta(days=365), today, False)
    else:
        diff = calculate_date - today
        verb = "until"
    output = str()
    mills = 0
    centuries = 0
    decades = 0
    years = 0
    days = abs(diff.days)

    unit = str()
    if days > 365250:
        mills = diff.days / 365250
        days -= mills * 365250

        if mills == 1: unit = "millennium"
        else: unit = "millenniums"
        if mills:
            output += "%s %s, " % (str(mills), unit)
    if days > 36525:
        centuries = days / 36525
        days -= centuries * 36525

        if centuries == 1: unit = "century"
        else: unit = "centuries"
        if centuries:
            output += "%s %s, " % (str(centuries), unit)
    if days > 3652:
        decades = days / 3652
        days -= decades * 3652

        if decades == 1: unit = "decade"
        else: unit = "decades"
        if decades:
            output += "%s %s, " % (str(decades), unit)
    if days > 365:
        years = days / 365
        days -= years * 365

        if years == 1: unit = "year"
        else: unit = "years"
        if years:
            output += "%s %s, " % (str(years), unit)

    if days:
        if days == 1: unit = "day"
        else: unit = "days"
        output += "%s %s, " % (str(days), unit)

    hours = diff.seconds / 3600
    if hours:
        if hours == 1: unit = "hour"
        else: unit = "hours"
        output += "%s %s, " % (str(hours), unit)

    minutes = (diff.seconds/60 - hours * 60)
    if minutes:
        if minutes > 1: unit = "minutes"
        elif minutes == 1: unit = "minute"
        output += "%s %s, " % (str(minutes), unit)

    seconds = (diff.seconds/60.0 - hours * 60) - (diff.seconds/60 - hours * 60)
    seconds *= 60.0
    seconds = int(seconds)
    if seconds:
        if seconds > 1: unit = 'seconds'
        elif seconds == 1: unit = 'second'
        output += '%s %s, ' % (str(seconds), unit)

    if output and output[0] == "-":
        output = output[1:]

    #output += ending % (verb, year.zfill(4), month.zfill(2), day.zfill(2), offset.zfill(2))
    return '%s%s' % (output, verb)


def two(inc):
    return str(inc).zfill(2)
def three(inc):
    return str(inc).zfill(3)


def generic_countdown(jenni, input):
    """ .countdown <year> <month> <day> - displays a countdown to a given date. """
    ending = "%s %s-%s-%sT%s"
    text = input.group(2)

    if text and len(text.split()) >= 3:
        text = input.group(2).split()
        year = text[0]
        month = text[1]
        day = text[2]

        if not year.isdigit() and not month.isdigit() and not day.isdigit():
            return jenni.reply('What are you even trying to do?')

        try:
            offset = text[3]
        except:
            offset = 0
    else:
        if text:
            offset = text.split()[0]
        else:
            offset = 0
        year = str(int(datetime.now().year) + 1)
        month = '01'
        day = '01'

    try:
        float(offset)
    except:
        #return jenni.reply(':-(')
        offset = 0


    if text and len(text) >= 3 and year.isdigit() and month.isdigit() and day.isdigit():
        calculate_date = datetime(int(year), int(month), int(day), 0, 0, 0)
        if abs(float(offset)) >= 14:
            return jenni.reply('Do you not love me anymore?')
        today = datetime.now() + timedelta(hours=float(offset))
        nye = False
    elif -14 <= int(offset) <= 14:
        if len(input) <= 3:
            offset = 0
        else:
            offset = offset
        calculate_date = datetime(int(datetime.now().year) + 1, 1, 1, 0, 0, 0)
        today = datetime.now() + timedelta(hours=int(offset))
        nye = True
    else:
        return jenni.say(bad_format)

    output = get_output(calculate_date, today, nye)

    if offset == 0:
        off = '00'
    else:
        if offset[0] == '+' or offset[0] == '-':
            offset = offset[1:]

        prefix = str()
        if float(offset) >= 0:
            prefix = '+'
        else:
            prefix = '-'

        if float(offset) % 1 == 0:
            off = '%s%s00' % (prefix, two(offset))
        else:
            parts = str(offset).split('.')
            wholenum = parts[0]
            first_part = two(wholenum)
            second_part = int(float('.%s' % parts[1]) * 60.0)
            second_part = two(second_part)
            off = '%s%s%s' % (prefix, first_part, second_part)


    output = ending % (output, two(year), two(month), two(day), off)
    jenni.say(output)
generic_countdown.commands = ['countdown', 'cd', 'nye']
generic_countdown.priority = 'low'


if __name__ == '__main__':
    print __doc__.strip()

#!/usr/bin/env python
"""
countdown.py - jenni Countdown Module
Copyright 2011-2013, Michael Yanovich (yanovich.net)
Licensed under the Eiffel Forum License 2.

More info:
 * jenni: https://github.com/myano/jenni/
 * Phenny: http://inamidst.com/phenny/
"""

from datetime import datetime

bad_format = "Please use correct format: .countdown 2012 12 21"
## 2036 02 07

def generic_countdown(jenni, input):
    """ .countdown <year> <month> <day> - displays a countdown to a given date. """
    ending = "%s %s-%s-%sT0000Z"
    try:
        text = input.group(2).split()
        year = text[0]
        month = text[1]
        day = text[2]
        if len(text) == 3 and year.isdigit() and month.isdigit() and day.isdigit():
            calculate_date = datetime(int(year), int(month), int(day), 0, 0, 0)
            today = datetime.now()
            verb = str()
            if calculate_date <= today:
                diff = today - calculate_date
                verb = "since"
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

            minutes = diff.seconds/60 - diff.seconds/60/60 * 60
            if minutes:
                if minutes > 1: unit = "minutes"
                elif minutes == 1: unit = "minute"
                output += "%s %s, " % (str(minutes), unit)

            if output and output[0] == "-":
                output = output[1:]

            output += ending % (verb, year.zfill(4), month.zfill(2), day.zfill(2))
            jenni.reply(output)
        else:
            jenni.reply(bad_format)
    except:
        jenni.reply(bad_format)
generic_countdown.commands = ['countdown', 'cd']
generic_countdown.priority = 'low'


if __name__ == '__main__':
    print __doc__.strip()

#!/usr/bin/env python
'''
units.py - jenni Units Module
Copyright 2013, Michael Yanovich (yanovich.net)
Licensed under the Eiffel Forum License 2.

More info:
 * jenni: https://github.com/myano/jenni/
 * Phenny: http://inamidst.com/phenny/
'''

import re
import time
import web


def btc(jenni, input):
    '''.btc -- display the current prices for Bitcoins'''
    try:
        page = web.get('http://www.ounce.me/')
    except Exception, e:
        print time.time(), btc, e
        return jenni.reply('Failed to reach ounce.me')
    prices = re.compile('(?i)(Bitcoin.*?)\|').findall(page)
    updated = re.compile('<span class="date">(.*?)</span>').findall(page)
    response = ' | '.join(x.strip() for x in prices)
    response += ' -- Last updated at: %s EDT (-4 GMT)' % (updated[0])
    jenni.reply(response)
btc.commands = ['btc']
btc.example = '.btc'
btc.rate = 90


if __name__ == '__main__':
    print __doc__.strip()

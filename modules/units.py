#!/usr/bin/env python
'''
units.py - jenni Units Module
Copyright 2015, zzqw (zzqw@riseup.net)
Copyright 2013, Michael Yanovich (yanovich.net)
Licensed under the Eiffel Forum License 2.

More info:
 * jenni: https://github.com/myano/jenni/
 * Phenny: http://inamidst.com/phenny/
'''

from modules import unicode as uc
import datetime as dt
import json
import re
import time
import web

exchange_rates = dict()
last_check = dt.datetime.now()
exchanges = ['btce', 'rock', 'ripple', 'bitstamp', 'coinbase']


def btc_page():
    try:
        page = web.get('https://api.bitcoincharts.com/v1/markets.json')
    except Exception, e:
        print time.time(), e
        return False, 'Failed to reach bitcoincharts.com'
    return True, page

def btc_coinbase_page():
    try:
        page = web.get('https://coinbase.com/api/v1/currencies/exchange_rates')
    except Exception, e:
        print time.time(), e
        return False, 'Failed to reach coinbase.com'
    return True, page



def ppnum(num):
    return re.sub("(?!\..*)(\d)(?=(\d{3})+(?!\d))", r"\1,", "%.2f" % num)


def btc(jenni, input):
    '''.btc -- display the current prices for Bitcoins'''

    bytes = web.get('https://www.bitstamp.net/api/ticker/')
    result = json.loads(bytes)

    msg = "bitstamp: %s high: %s low: %s" % (
            result['last'],
            result['high'],
            result['low']
        )

    jenni.say(msg)


btc.commands = ['btc']
btc.example = '.btc'

def fbtc(jenni, input):
    try:
        page = web.get('http://thefuckingbitcoin.com/')
    except:
        return jenni.say('Could not access thefuckingbitcoin.com')
    price = re.search('<p id="lastPrice">(\S+)</p>', page)
    remarks = re.search('<p id="remark">(.*?)</p><p id="remarkL2">(.*?)</p>',
                        page)
    try:
        remarks = remarks.groups()
    except:
        return jenni.say('Could not find relevant information.')
    resp = str()
    resp += '1 BTC == %s USD. ' % price.groups()
    if remarks:
        resp += '%s %s' % (remarks[0], remarks[1])
    jenni.say(resp)
fbtc.commands = ['fbtc']
fbtc.example = '.fbtc'


if __name__ == '__main__':
    print __doc__.strip()

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


def btc_page():
    try:
        page = web.get('http://www.ounce.me/')
    except Exception, e:
        print time.time(), btc, e
        return False, 'Failed to reach ounce.me'
    return True, page

def usd_price():
    find_usd = re.compile('\$\d+\.\d+')
    status, page = btc_page()
    amounts = find_usd.findall(page)
    if amounts:
        amount = amounts[0][1:]
    try:
        amount = float(amount)
    except:
        amount = 0.0
    return amount

def ppnum(num):
    return re.sub("(?!\..*)(\d)(?=(\d{3})+(?!\d))", r"\1,", "%.2f" % num)


def find_float(num):
    try:
        out = float(num)
    except:
        out = 0
    return out


def btc(jenni, input):
    '''.btc -- display the current prices for Bitcoins'''
    txt = input.group(2)
    if txt:
        txt = txt.strip()
        amount = usd_price()
        txt = txt.replace(' ', '')
        float_inc = 0
        inc = txt.lower().replace('usd', '').replace('btc', '')
        float_inc = find_float(inc)
        if 'usd' in txt.lower() and 'btc' not in txt.lower():
            response = 'BTC: '
            response += str(ppnum(float_inc / amount))
        elif 'btc' in txt.lower() and 'usd' not in txt.lower():
            response = 'USD: '
            response += str(ppnum(float_inc * amount))
        else:
            response = 'Defaulting to, USD: '
            response += str(ppnum(float_inc * amount))
        if float_inc:
            jenni.reply(response)
        else:
            jenni.reply('I could not understand your input!')
    else:
        status, page = btc_page()
        if not status:
            jenni.reply(page)
        prices = re.compile('(?i)((?:Bitcoin|Mt).*?)\|').findall(page)
        updated = re.compile('<span class="date">(.*?)</span>').findall(page)
        amount = usd_price()
        response = ' | '.join(x.strip() for x in prices[:6])
        if usd_price:
            response += ' | Lolcat Index = $'
            lolcat = amount * 160
            total = ppnum(lolcat)
            response += str(total)
        response += ' -- Last updated at: %s EDT (-4 GMT)' % (updated[0])
        jenni.reply(response)
btc.commands = ['btc']
btc.example = '.btc'
btc.rate = 90


if __name__ == '__main__':
    print __doc__.strip()

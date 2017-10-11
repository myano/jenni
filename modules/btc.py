#!/usr/bin/env python
'''
units.py - jenni Units Module
Copyright 2013, Michael Yanovich (yanovich.net)
Licensed under the Eiffel Forum License 2.

More info:
 * jenni: https://github.com/myano/jenni/
 * Phenny: http://inamidst.com/phenny/
'''

from modules import proxy
import web
from modules import unicode as uc
import datetime as dt
import json
import re

btc_exchange_rates = dict()
bcc_exchange_rates = dict()
last_check_btc = dt.datetime.now()
last_check_bcc = dt.datetime.now()

btc_exchanges = ['btce', 'rock', 'bitstamp', 'coinbase']


def btc_page():
    try:
        page = web.get('https://api.bitcoincharts.com/v1/markets.json')
    except Exception, e:
        print dt.datetime.now(), e
        return False, 'Failed to reach bitcoincharts.com'
    return True, page


def btc_coinbase_page():
    try:
        page = web.get('https://coinbase.com/api/v1/currencies/exchange_rates')
    except Exception, e:
        print dt.datetimenow.now(), e
        return False, 'Failed to reach coinbase.com'
    return True, page


def ppnum(num):
    return re.sub("(?!\..*)(\d)(?=(\d{3})+(?!\d))", r"\1,", "%.2f" % num)


def btc(jenni, input):
    '''.btc -- display the current prices for Bitcoins'''
    global btc_exchange_rates
    global last_check_btc

    now = dt.datetime.now()

    if (not btc_exchange_rates) or (now - last_check_btc > dt.timedelta(minutes=15)):
        status, page = btc_page()
        json_page = dict()

        if status:
            try:
                json_page = json.loads(page)
            except:
                pass

        else:
            return jenni.reply(page)

        if 'USD' not in btc_exchange_rates:
            btc_exchange_rates['USD'] = dict()
        ## build internal state of exchange
        for each in json_page:
            if each['currency'] == 'USD':
                if 'USD' not in btc_exchange_rates:
                    btc_exchange_rates['USD'] = dict()
                btc_exchange_rates['USD'][each['symbol'].replace('USD', '')] = each['close']
        last_check_btc = dt.datetime.now()

        coinbase_status, coinbase_page = btc_coinbase_page()

        coinbase_json = dict()

        try:
            coinbase_json = json.loads(coinbase_page)
        except:
            #return jenni.say('Could not parse json from coinbase API.')
            pass

        if coinbase_json:
            btc_exchange_rates['USD']['coinbase'] = ppnum(float(coinbase_json['btc_to_usd']))

    response = '\x02\x0304One (1) Bitcoin (BTC) in USD\x03:\x02 '
    symbols = btc_exchange_rates['USD'].keys()
    symbols.sort()

    for each in symbols:
        if each.replace('USD', '') in btc_exchanges:
            fix_var = str(btc_exchange_rates['USD'][each]).replace(",", '')
            fix_var = float(fix_var)
            fix_var = ppnum(fix_var)
            response += '\x1F{0}\x1F: ${1} | '.format(each.title(), fix_var)

    coinbase_rate = str(btc_exchange_rates['USD']['coinbase']).replace(',', '')
    coinbase_rate = float(coinbase_rate)

    response += '\x1Flolcat\x1F (coinbase) index: ${0} | '.format(ppnum(160.0 * coinbase_rate))
    response += '\x1FHowells\x1F (coinbase) index: ${0} | '.format(ppnum(7500.0 * coinbase_rate))

    temp_time = last_check_btc.strftime('%Y-%m-%d %H:%M')
    response += '\x02Last updated\x02 at: {0} UTC'.format(temp_time)

    jenni.say(response)
btc.commands = ['btc']
btc.example = '.btc'
btc.rate = 20


def fbtc(jenni, input):
    '''.fbtc - returns prices from "The Fucking Bitcoin"'''
    try:
        page = proxy.get('http://thefuckingbitcoin.com/')
    except:
        return jenni.say('Could not access thefuckingbitcoin.com')

    price = re.search('<p id="lastPrice">(\S+)</p>', page)
    remarks = re.search('<p id="remark">(.*?)</p><p id="remarkL2">(.*?)</p>', page)

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
fbtc.rate = 20


def bitfinex_retrieve(page):
    bitfinex_json = json.loads(page)
    return bitfinex_json[-4]


def bcc(jenni, input):
    '''.bcc -- display the current prices for Bitcoin Cash'''
    global last_check_bcc
    global bcc_exchange_rates

    now = dt.datetime.now()
    response = '\x02\x0303One (1) Bitcoin Cash (BCH) in USD:\x03\x02 '

    bcc_exchanges = {
            'Bitfinex': ['https://api.bitfinex.com/v2/ticker/tBCHUSD', lambda x: json.loads(x)[-4]],
            'Bittrex': ['https://bittrex.com/api/v1.1/public/getticker?market=USDT-BCC', lambda x: json.loads(x)['result']['Last']],
            'CoinMarketCap': ['https://api.coinmarketcap.com/v1/ticker/bitcoin-cash/', lambda x: json.loads(x)[0]['price_usd']],
        }

    exchanges_status = list()

    if (not bcc_exchange_rates) or (now - last_check_bcc > dt.timedelta(minutes=15)):

        for bcc_exchange in bcc_exchanges:
            try:
                bcc_page = web.get(bcc_exchanges[bcc_exchange][0])
            except:
                exchanges_status.append(False)
                continue

            try:
                exchange_price = bcc_exchanges[bcc_exchange][1](bcc_page)
            except:
                exchanges_status.append(False)
                continue

            exchanges_status.append(True)

            bcc_exchange_rates[bcc_exchange] = exchange_price
            last_check_bcc = dt.datetime.now()

        if not any(exchanges_status):
            return jenni.say('We could not access any of the APIs.')

    for exchange in bcc_exchange_rates:
        response += '\x1F{0}\x1F: ${1:.2f}, '.format(exchange, round(float(bcc_exchange_rates[exchange]), 2))

    temp_time = last_check_bcc.strftime('%Y-%m-%d %H:%M')
    response += '\x02Last updated\x02 at: {0} UTC'.format(temp_time)

    #print "exchanges_status:", exchanges_status
    jenni.say(response)
bcc.commands = ['bcc']


if __name__ == '__main__':
    print __doc__.strip()

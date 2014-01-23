#!/usr/bin/env python
# vim: set fileencoding=UTF-8 :
"""
weather.py - jenni Weather Module
Copyright 2009-2013, Michael Yanovich (yanovich.net)
Copyright 2008-2013, Sean B. Palmer (inamidst.com)
Licensed under the Eiffel Forum License 2.

More info:
 * jenni: https://github.com/myano/jenni/
 * Phenny: http://inamidst.com/phenny/
"""

import json
import re
import urllib
import web
from tools import deprecated
from modules import latex
from modules import unicode as uc
from icao import data

r_from = re.compile(r'(?i)([+-]\d+):00 from')
r_tag = re.compile(r'<(?!!)[^>]+>')
re_line = re.compile('<small>1</small>(.*)')
re_lat = re.compile('<span class="latitude">(\S+)</span>')
re_long = re.compile('<span class="longitude">(\S+)</span>')
cnty = re.compile('<a href="/countries/\S+\.html">(.+)</a>')
city = re.compile('<a href="/maps/\S+">(.+)</a>')


def clean(txt):
    '''Remove HTML entities from a given text'''
    return r_tag.sub('', txt)


def location(name):
    name = urllib.quote(name.encode('utf-8'))
    uri = "http://www.geonames.org/search.html?q=%s" % (name)
    if re.match('\d{5}', name):
        uri += '&country=us'
    page = web.get(uri)

    unknown = ('?', '?', '0', '0')

    line = re_line.findall(page)
    if not line:
        return unknown
    line = line[0]

    find_lat = re_lat.findall(line)

    find_lng = re_long.findall(line)

    find_cnty = cnty.findall(line)

    find_city = city.findall(line)


    if find_lng and find_lat and find_cnty and find_city:
        name = clean(find_city[0])
        countryName = clean(find_cnty[0])
        lat = clean(find_lat[0])
        lng = clean(find_lng[0])
    else:
        return unknown

    return name, countryName, lat, lng


class GrumbleError(object):
    pass


def local(icao, hour, minute):
    uri = ('http://www.flightstats.com/' +
             'go/Airport/airportDetails.do?airportCode=%s')
    try: bytes = web.get(uri % icao)
    except AttributeError:
        raise GrumbleError('A WEBSITE HAS GONE DOWN WTF STUPID WEB')
    m = r_from.search(bytes)
    if m:
        offset = m.group(1)
        lhour = int(hour) + int(offset)
        lhour = lhour % 24
        return (str(lhour) + ':' + str(minute) + ', ' + str(hour) +
                  str(minute) + 'Z')
    return str(hour) + ':' + str(minute) + 'Z'


def code(jenni, search):

    if search.upper() in data:
        return search.upper()
    else:
        name, country, latitude, longitude = location(search)
        if name == '?': return False
        sumOfSquares = (99999999999999999999999999999, 'ICAO')
        for icao_code in data:
            lat = float(data[icao_code][0])
            lon = float(data[icao_code][1])
            latDiff = abs(float(latitude) - float(lat))
            lonDiff = abs(float(longitude) - float(lon))
            diff = (latDiff * latDiff) + (lonDiff * lonDiff)
            if diff < sumOfSquares[0]:
                sumOfSquares = (diff, icao_code)
        return sumOfSquares[1]


def get_metar(icao_code):
    '''Obtain METAR data from NOAA for a given ICAO code'''

    uri = 'http://weather.noaa.gov/pub/data/observations/metar/stations/%s.TXT'

    try:
        page = web.get(uri % icao_code)
    except AttributeError:
        raise GrumbleError('OH CRAP NOAA HAS GONE DOWN THE WEB IS BROKEN')
    if 'Not Found' in page:
        return False, icao_code + ': no such ICAO code, or no NOAA data.'

    return True, page


def get_icao(jenni, inc, command='weather'):
    '''Provide the ICAO code for a given input'''

    if not inc:
        return False, 'Try .%s London, for example?' % (command)

    icao_code = code(jenni, inc)

    if not icao_code:
        return False, 'No ICAO code found, sorry.'

    return True, icao_code


def show_metar(jenni, input):
    '''.metar <location> -- shows the raw METAR data for a given location'''
    txt = input.group(2)

    if not txt:
        return jenni.say('Try .metar London, for example?')

    status, icao_code = get_icao(jenni, txt, 'metar')
    if not status:
        return jenni.say(icao_code)

    status, metar = get_metar(icao_code)
    if not status:
        return jenni.say(metar)

    return jenni.say(metar)
show_metar.commands = ['metar']
show_metar.example = '.metar London'
show_metar.priority = 'low'


def f_weather(jenni, input):
    """.weather <ICAO> - Show the weather at airport with the code <ICAO>."""

    text = input.group(2)

    status, icao_code = get_icao(jenni, text)
    if not status:
        return jenni.say(icao_code)

    status, page = get_metar(icao_code)
    if not status:
        return jenni.say(page)

    metar = page.splitlines().pop()
    metar = metar.split(' ')

    if len(metar[0]) == 4:
        metar = metar[1:]

    if metar[0].endswith('Z'):
        time = metar[0]
        metar = metar[1:]
    else: time = None

    if metar[0] == 'AUTO':
        metar = metar[1:]
    if metar[0] == 'VCU':
        jenni.say(icao_code + ': no data provided')
        return

    if metar[0].endswith('KT'):
        wind = metar[0]
        metar = metar[1:]
    else: wind = None

    if ('V' in metar[0]) and (metar[0] != 'CAVOK'):
        vari = metar[0]
        metar = metar[1:]
    else: vari = None

    if ((len(metar[0]) == 4) or
         metar[0].endswith('SM')):
        visibility = metar[0]
        metar = metar[1:]
    else: visibility = None

    while metar[0].startswith('R') and (metar[0].endswith('L')
                                                or 'L/' in metar[0]):
        metar = metar[1:]

    if len(metar[0]) == 6 and (metar[0].endswith('N') or
                                        metar[0].endswith('E') or
                                        metar[0].endswith('S') or
                                        metar[0].endswith('W')):
        metar = metar[1:] # 7000SE?

    cond = []
    while (((len(metar[0]) < 5) or
             metar[0].startswith('+') or
             metar[0].startswith('-')) and (not (metar[0].startswith('VV') or
             metar[0].startswith('SKC') or metar[0].startswith('CLR') or
             metar[0].startswith('FEW') or metar[0].startswith('SCT') or
             metar[0].startswith('BKN') or metar[0].startswith('OVC')))):
        cond.append(metar[0])
        metar = metar[1:]

    while '/P' in metar[0]:
        metar = metar[1:]

    if not metar:
        return jenni.say(icao_code + ': no data provided')

    cover = []
    while (metar[0].startswith('VV') or metar[0].startswith('SKC') or
             metar[0].startswith('CLR') or metar[0].startswith('FEW') or
             metar[0].startswith('SCT') or metar[0].startswith('BKN') or
             metar[0].startswith('OVC')):
        cover.append(metar[0])
        metar = metar[1:]
        if not metar:
            return jenni.say(icao_code + ': no data provided')

    if metar[0] == 'CAVOK':
        cover.append('CLR')
        metar = metar[1:]

    if metar[0] == 'PRFG':
        cover.append('CLR') # @@?
        metar = metar[1:]

    if metar[0] == 'NSC':
        cover.append('CLR')
        metar = metar[1:]

    if ('/' in metar[0]) or (len(metar[0]) == 5 and metar[0][2] == '.'):
        temp = metar[0]
        metar = metar[1:]
    else: temp = None

    if metar[0].startswith('QFE'):
        metar = metar[1:]

    if metar[0].startswith('Q') or metar[0].startswith('A'):
        pressure = metar[0]
        metar = metar[1:]
    else: pressure = None

    if time:
        hour = time[2:4]
        minute = time[4:6]
        time = local(icao_code, hour, minute)
    else: time = '(time unknown)'

    speed = False

    if wind:
        try:
            speed = float(wind[3:5])
        except:
            speed = 0

        if speed < 1:
            description = 'Calm'
        elif speed < 4:
            description = 'Light air'
        elif speed < 7:
            description = 'Light breeze'
        elif speed < 11:
            description = 'Gentle breeze'
        elif speed < 16:
            description = 'Moderate breeze'
        elif speed < 22:
            description = 'Fresh breeze'
        elif speed < 28:
            description = 'Strong breeze'
        elif speed < 34:
            description = 'Near gale'
        elif speed < 41:
            description = 'Gale'
        elif speed < 48:
            description = 'Strong gale'
        elif speed < 56:
            description = 'Storm'
        elif speed < 64:
            description = 'Violent storm'
        else: description = 'Hurricane'

        degrees = wind[0:3]
        if degrees == 'VRB':
            degrees = u'\u21BB'.encode('utf-8')
        elif (degrees <= 22.5) or (degrees > 337.5):
            degrees = u'\u2191'.encode('utf-8')
        elif (degrees > 22.5) and (degrees <= 67.5):
            degrees = u'\u2197'.encode('utf-8')
        elif (degrees > 67.5) and (degrees <= 112.5):
            degrees = u'\u2192'.encode('utf-8')
        elif (degrees > 112.5) and (degrees <= 157.5):
            degrees = u'\u2198'.encode('utf-8')
        elif (degrees > 157.5) and (degrees <= 202.5):
            degrees = u'\u2193'.encode('utf-8')
        elif (degrees > 202.5) and (degrees <= 247.5):
            degrees = u'\u2199'.encode('utf-8')
        elif (degrees > 247.5) and (degrees <= 292.5):
            degrees = u'\u2190'.encode('utf-8')
        elif (degrees > 292.5) and (degrees <= 337.5):
            degrees = u'\u2196'.encode('utf-8')

        if not icao_code.startswith('EN') and not icao_code.startswith('ED'):
            ## for any part of the world except Germany and Norway
            wind = '%s %.1fkt (%s)' % (description, speed, degrees)
        elif icao_code.startswith('ED'):
            ## Germany
            kmh = float(speed * 1.852)
            wind = '%s %.1fkm/h (%.1fkt) (%s)' % (description, kmh, speed, degrees)
        elif icao_code.startswith('EN'):
            ## Norway
            ms = float(speed * 0.514444444)
            wind = '%s %.1fm/s (%.1fkt) (%s)' % (description, ms, speed, degrees)
    else: wind = '(wind unknown)'

    if visibility:
        visibility = visibility + 'm'
    else: visibility = '(visibility unknown)'

    if cover:
        level = None
        for c in cover:
            if c.startswith('OVC') or c.startswith('VV'):
                if (level is None) or (level < 8):
                    level = 8
            elif c.startswith('BKN'):
                if (level is None) or (level < 5):
                    level = 5
            elif c.startswith('SCT'):
                if (level is None) or (level < 3):
                    level = 3
            elif c.startswith('FEW'):
                if (level is None) or (level < 1):
                    level = 1
            elif c.startswith('SKC') or c.startswith('CLR'):
                if level is None:
                    level = 0

        if level == 8:
            cover = u'Overcast \u2601'.encode('utf-8')
        elif level == 5:
            cover = 'Cloudy'
        elif level == 3:
            cover = 'Scattered'
        elif (level == 1) or (level == 0):
            cover = u'Clear \u263C'.encode('utf-8')
        else: cover = 'Cover Unknown'
    else: cover = 'Cover Unknown'

    if temp:
        if '/' in temp:
            t = temp.split('/')
            temp = t[0]
            dew = t[1]
        else: temp = temp.split('.')[0]
        if temp.startswith('M'):
            temp = '-' + temp[1:]
        if dew.startswith('M'):
            dew = '-' + dew[1:]
        try:
            temp = float(temp)
            dew = float(dew)
        except ValueError:
            temp = '?'
            dew = '?'
    else:
        temp = '?'
        dew = '?'

    windchill = False
    if isinstance(temp, float) and isinstance(speed, float) and temp <= 10.0 and speed > 0:
        speed_kmh = speed * 1.852
        windchill = 13.12 + (0.6215 * temp) - (11.37 * (speed_kmh ** (0.16))) + (0.3965 * temp * (speed_kmh ** (0.16)))
        windchill = float(windchill)
        f = (windchill * 1.8) + 32
        if icao_code.startswith('K'):
            ## if in North America
            windchill = u'%.1f\u00B0F (%.1f\u00B0C)'.encode('utf-8') % (f, windchill)
        else:
            windchill = u'%.1f\u00B0C'.encode('utf-8') % (windchill)

    if pressure:
        if pressure.startswith('Q'):
            pressure = pressure.lstrip('Q')
            if pressure != 'NIL':
                pressure = str(float(pressure)) + 'mb'
            else: pressure = '?mb'
        elif pressure.startswith('A'):
            pressure = pressure.lstrip('A')
            if pressure != 'NIL':
                inches = pressure[:2] + '.' + pressure[2:]
                mb = float(inches) * 33.7685
                pressure = '%sin (%.2fmb)' % (inches, mb)
            else: pressure = '?mb'

            if isinstance(temp, float):
                f = (temp * 1.8) + 32
                temp = u'%.1f\u00B0F (%.1f\u00B0C)'.encode('utf-8') % (f, temp)
            if isinstance(dew, float):
                f = (dew * 1.8) + 32
                dew = u'%.1f\u00B0F (%.1f\u00B0C)'.encode('utf-8') % (f, dew)
    else: pressure = '?mb'

    if isinstance(temp, float):
        temp = u'%.1f\u00B0C'.encode('utf-8') % temp
    if isinstance(dew, float):
        dew = u'%.1f\u00B0C'.encode('utf-8') % dew

    if cond:
        conds = cond
        cond = ''

        intensities = {
            '-': 'Light',
            '+': 'Heavy'
        }

        descriptors = {
            'MI': 'Shallow',
            'PR': 'Partial',
            'BC': 'Patches',
            'DR': 'Drifting',
            'BL': 'Blowing',
            'SH': 'Showers of',
            'TS': 'Thundery',
            'FZ': 'Freezing',
            'VC': 'In the vicinity:',
            'RA': 'Unimaginable',
        }

        phenomena = {
            'DZ': 'Drizzle',
            'RA': 'Rain',
            'SN': 'Snow',
            'SG': 'Snow Grains',
            'IC': 'Ice Crystals',
            'PL': 'Ice Pellets',
            'GR': 'Hail',
            'GS': 'Small Hail',
            'UP': 'Unknown Precipitation',
            'BR': 'Mist',
            'FG': 'Fog',
            'FU': 'Smoke',
            'VA': 'Volcanic Ash',
            'DU': 'Dust',
            'SA': 'Sand',
            'HZ': 'Haze',
            'PY': 'Spray',
            'PO': 'Whirls',
            'SQ': 'Squalls',
            'FC': 'Tornado',
            'SS': 'Sandstorm',
            'DS': 'Duststorm',
            # ? Cf. http://swhack.com/logs/2007-10-05#T07-58-56
            'TS': 'Thunderstorm',
            'SH': 'Showers'
        }

        for c in conds:
            if c.endswith('//'):
                if cond: cond += ', '
                cond += 'Some Precipitation'
            elif len(c) == 5:
                intensity = intensities[c[0]]
                descriptor = descriptors[c[1:3]]
                phenomenon = phenomena.get(c[3:], c[3:])
                if cond: cond += ', '
                cond += intensity + ' ' + descriptor + ' ' + phenomenon
            elif len(c) == 4:
                descriptor = descriptors.get(c[:2], c[:2])
                phenomenon = phenomena.get(c[2:], c[2:])
                if cond: cond += ', '
                cond += descriptor + ' ' + phenomenon
            elif len(c) == 3:
                intensity = intensities.get(c[0], c[0])
                phenomenon = phenomena.get(c[1:], c[1:])
                if cond: cond += ', '
                cond += intensity + ' ' + phenomenon
            elif len(c) == 2:
                phenomenon = phenomena.get(c, c)
                if cond: cond += ', '
                cond += phenomenon

    output = str()
    output += 'Cover: ' + cover
    output += ', Temp: ' + str(temp)
    output += ', Dew Point: ' + str(dew)
    if windchill:
        output += ', Windchill: ' + str(windchill)
    output += ', Pressure: ' + pressure
    if cond:
        output += ' Condition: ' + cond
    output += ', Wind: ' + wind
    output += ' - %s, %s' % (str(icao_code), time)


    jenni.say(output)
f_weather.rule = (['weather', 'wx'], r'(.*)')


def fucking_weather(jenni, input):
    """.fw (ZIP|City, State) -- provide a ZIP code or a city state pair to hear about the fucking weather"""
    text = input.group(2)
    if not text:
        jenni.reply('INVALID FUCKING INPUT. PLEASE ENTER A FUCKING ZIP CODE, OR A FUCKING CITY-STATE PAIR.')
        return
    new_text = str()

    new_text = uc.encode(text)
    search = urllib.quote((new_text).strip())

    url = 'http://thefuckingweather.com/?where=%s' % (search)
    try:
        page = web.get(url)
    except:
        return jenni.say("I COULDN'T ACCESS THE FUCKING SITE.")
    re_mark = re.compile('<p class="remark">(.*?)</p>')
    re_temp = re.compile('<span class="temperature" tempf="\S+">(\S+)</span>')
    re_condition = re.compile('<p class="large specialCondition">(.*?)</p>')
    re_flavor = re.compile('<p class="flavor">(.*?)</p>')
    re_location = re.compile('<span id="locationDisplaySpan" class="small">(.*?)</span>')
    temps = re_temp.findall(page)
    remarks = re_mark.findall(page)
    conditions = re_condition.findall(page)
    flavor = re_flavor.findall(page)
    location = re_location.findall(page)
    response = str()
    if location and location[0]:
        response += location[0] + ': '
    if temps:
        tempf = float(temps[0])
        tempc = (tempf - 32.0) * (5 / 9.0)
        response += u'%.1f°F?! %.1f°C?! ' % (tempf, tempc)
    if remarks:
        response += remarks[0]
    else:
        response += "I CAN'T FIND THAT SHIT ON THEIR PAGE."
    if conditions:
        response += ' ' + conditions[0]
    if flavor:
        response += ' -- ' + flavor[0].replace('  ', ' ')
    jenni.say(response)
fucking_weather.commands = ['fucking_weather', 'fw']
fucking_weather.priority = 'low'
fucking_weather.rate = 5


def windchill(jenni, input):
    '''.windchill <temp> <wind speed> -- shows Windchill in F'''
    text = input.split()
    if len(text) == 1:
        return jenni.say(u'.windchill <temp> <wind speed> -- shows Windchill in \u00B0F')
    if len(text) >= 3:
        try:
            temp = float(text[1])
            wind = float(text[2])
        except:
            return jenni.say('Invalid arguments! Try, .windchill without any parameters.')

    if temp > 50:
        return jenni.say(u'The windchill formula only works on temperatures below 50 \u00B0F')

    if wind < 0:
        return jenni.say("You can't have negative wind speed!")
    elif wind >= 300:
        jenni.reply('Are you okay?')

    ## cf. http://is.gd/mgLuzU
    wc = 35.74 + (0.6215 * temp) - (35.75 * (wind ** (0.16))) + (0.4275 * temp * (wind ** (0.16)))

    jenni.say(u'Windchill: %2.f \u00B0F' % (wc))
windchill.commands = ['windchill', 'wc']
windchill.priority = 'low'

if __name__ == '__main__':
    print __doc__.strip()

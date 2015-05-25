#!/usr/bin/env python
"""
info.py - jenni Information Module
Copyright 2009-2013, Michael Yanovich (yanovich.net)
Copyright 2008-2013, Sean B. Palmer (inamidst.com)
Licensed under the Eiffel Forum License 2.

More info:
 * jenni: https://github.com/myano/jenni/
 * Phenny: http://inamidst.com/phenny/
"""

from itertools import izip_longest

def fchannels():
    try:
        f = open("nochannels.txt", "r")
    except:
        return False
    lines = f.readlines()[0]
    f.close()
    lines = lines.replace('\n', '')
    return lines.split(',')


def doc(jenni, input):
    """Shows a command's documentation, and possibly an example."""
    if input.group(1) == "help":
        name = input.group(2)
    else:
        name = input.group(1)
    name = name.lower()

    if name in jenni.doc:
        jenni.reply(jenni.doc[name][0])
        if jenni.doc[name][1]:
            jenni.say('e.g. ' + jenni.doc[name][1])
doc.rule = '(?i)$nick[,:]\s(?:help|doc) +([A-Za-z]+)(?:\?+)?$'
doc.example = '$nickname: doc tell?'
doc.priority = 'low'


def commands(jenni, input):
    common_commands = "Common commands: join <channel> - Join the provided channel. (admin only); part <channel> - Leave the provided channel. (admin only); animate_me, nm8_me <search term> - Find an animated gif from giphy.com; py, python <python> - Interpret some Python (runs on Google App Engine); s/<find>/<replace> - Not a command, jenni will listen for phrases beginning with s/ and perform basic find-replace functionality. Note that this is not PRE compliant; .food <location> - Find food in your area using the Yelp API; img_me, image_me <search term> - Provide a random result from the first page of Google Image search; commands, help - Display a list of all commands, ip, iplookup, host <ip|host> - Get approximate geolocation from an IP or host using freegeoip.net; mustache_me <search term> - Adds a mustache to the image returned for the given search term; reload <module>: Ask jenni to reload a module. (admin only), bing <search query> - Provides the first result from a Bing search; duck, ddg <search query> - Provides the first link from a DuckDuckGo search; g - <query> - Google for <query> and return the top result; search <search query> - Provides the first result from Bing, DuckDuckgo, and Google; tell, to <person> <message> - relays a message to a person the next time they say something anywhere jenni is present; w, wik, wiki <entry> - Returns the wiki entry for <entry>; xkcd - Randomly generates a valid URL for an xkcd item."

    jenni.reply("I'm sending you a list of my most common commands in private.")
    jenni.reply('For a list of all of my commands, please visit: https://is.gd/CPStvK')

    common_split = izip_longest(*[iter(common_commands)]*445, fillvalue='')
    for split_commands in common_split:
        jenni.msg(input.nick, ''.join(split_commands), False, False, 1)

commands.commands = ['commands', 'help']
commands.priority = 'low'


def help(jenni, input):
    response = (
        'Hi, I\'m a bot. Say ".commands" to me in private for a list ' +
        'of my commands, or see https://github.com/myano/jenni/wiki for more ' +
        'general details. My owner is %s.'
    ) % jenni.config.owner
    jenni.reply(response)
help.rule = ('$nick', r'(?i)help(?:[?!]+)?$')
help.priority = 'low'


def stats(jenni, input):
    """Show information on command usage patterns."""
    if input.sender == '##uno':
        return
    commands = dict()
    users = dict()
    channels = dict()


    ignore = set(['f_note', 'startup', 'message', 'noteuri',
                  'say_it', 'collectlines', 'oh_baby', 'chat',
                  'collect_links', 'bb_collect', 'random_chat'])
    for (name, user), count in jenni.stats.iteritems():
        if name in ignore:
            continue
        if not user:
            continue

        if not user.startswith('#'):
            try:
                users[user] += count
            except KeyError:
                users[user] = count
        else:
            try:
                commands[name] += count
            except KeyError:
                commands[name] = count

            try:
                channels[user] += count
            except KeyError:
                channels[user] = count

    comrank = sorted([(b, a) for (a, b) in commands.iteritems()], reverse=True)
    userank = sorted([(b, a) for (a, b) in users.iteritems()], reverse=True)
    charank = sorted([(b, a) for (a, b) in channels.iteritems()], reverse=True)

    # most heavily used commands
    creply = 'most used commands: '
    for count, command in comrank[:10]:
        creply += '%s (%s), ' % (command, count)
    jenni.say(creply.rstrip(', '))

    # most heavy users
    reply = 'power users: '
    k = 1
    for count, user in userank:
        if ' ' not in user and '.' not in user:
            reply += '%s (%s), ' % (user, count)
            k += 1
            if k > 10:
                break
    jenni.say(reply.rstrip(', '))

    # most heavy channels
    chreply = 'power channels: '
    bchannels = fchannels()
    for count, channel in charank[:3]:
        if bchannels and channel in bchannels:
            continue
        chreply += '%s (%s), ' % (channel, count)
    jenni.say(chreply.rstrip(', '))
stats.commands = ['stats']
stats.priority = 'low'

if __name__ == '__main__':
    print __doc__.strip()

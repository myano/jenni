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


def fchannels():
    f = open("nochannels.txt", "r")
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
    # This function only works in private message
    #if input.sender.startswith('#'): return
    if input.group(1) == "help" and input.group(2):
        doc(jenni, input)
        return
    names = ', '.join(sorted(jenni.doc.iterkeys()))
    jenni.reply("I am sending you a private message of all my commands!")
    jenni.reply('For more robust help please see: http://is.gd/CPStvK')
    jenni.msg(input.nick, 'Commands I recognise: ' + names + '.')
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
    bchannels = fchannels()

    ignore = set(['f_note', 'startup', 'message', 'noteuri',
                  'say_it', 'collectlines', 'oh_baby', 'chat',
                  'collect_links', 'bb_collect'])
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
    for count, channel in charank[:3]:
        if channel in bchannels:
            continue
        chreply += '%s (%s), ' % (channel, count)
    jenni.say(chreply.rstrip(', '))
stats.commands = ['stats']
stats.priority = 'low'

if __name__ == '__main__':
    print __doc__.strip()

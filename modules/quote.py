#!/usr/bin/env python
"""
quote.py - jenni Quote Module
Copyright 2008-2013, Michael Yanovich (yanovich.net)
Licensed under the Eiffel Forum License 2.

More info:
 * jenni: https://github.com/myano/jenni/
 * Phenny: http://inamidst.com/phenny/
"""

import random
from modules import unicode as uc

def write_addquote(text):
    fn = open('quotes.txt', 'a')
    output = uc.encode(text)
    fn.write(output)
    fn.write('\n')
    fn.close()


def addquote(jenni, input):
    '''.addquote <nick> something they said here -- adds the quote to the quote database.'''
    text = input.group(2)
    if not text:
        return jenni.say('No quote provided')

    write_addquote(text)

    jenni.reply('Quote added.')
addquote.commands = ['addquote']
addquote.priority = 'low'
addquote.example = '.addquote'


def retrievequote(jenni, input):
    '''.quote <number> -- displays a given quote'''
    NO_QUOTES = 'There are currently no quotes saved.'
    text = input.group(2)
    try:
        fn = open('quotes.txt', 'r')
    except:
        return jenni.reply('Please add a quote first.')

    lines = fn.readlines()
    if len(lines) < 1:
        return jenni.reply(NO_QUOTES)
    MAX = len(lines)
    fn.close()
    random.seed()
    try:
        number = int(text)
        if number < 0:
            number = MAX - abs(number) + 1
    except:
        number = random.randint(1, MAX)
    if not (0 <= number <= MAX):
        jenni.reply("I'm not sure which quote you would like to see.")
    else:
        if lines:
            if number == 0:
                return jenni.say('There is no "0th" quote!')
            else:
                line = lines[number - 1]
            jenni.say('Quote %s of %s: ' % (number, MAX) + line)
        else:
            jenni.reply(NO_QUOTES)
retrievequote.commands = ['quote']
retrievequote.priority = 'low'
retrievequote.example = '.quote'


def delquote(jenni, input):
    '''.rmquote <number> -- removes a given quote from the database. Can only be done by the owner of the bot.'''
    if not input.owner:
        return
    text = input.group(2)
    number = int()

    try:
        fn = open('quotes.txt', 'r')
    except:
        return jenni.reply('No quotes to delete.')

    lines = fn.readlines()
    MAX = len(lines)
    fn.close()

    try:
        number = int(text)
    except:
        jenni.reply('Please enter the quote number you would like to delete.')
        return

    if number > 0:
        newlines = lines[:number - 1] + lines[number:]
    elif number == 0:
        return jenni.reply('There is no "0th" quote!')
    elif number == -1:
        newlines = lines[:number]
    else:
        ## number < -1
        newlines = lines[:number] + lines[number + 1:]
    fn = open('quotes.txt', 'w')
    for line in newlines:
        txt = line
        if txt:
            fn.write(txt)
            if txt[-1] != '\n':
                fn.write('\n')
    fn.close()
    jenni.reply('Successfully deleted quote %s.' % (number))
delquote.commands = ['rmquote', 'delquote']
delquote.priority = 'low'
delquote.example = '.rmquote'


def grabquote(jenni, input):
    try:
        from modules import find
    except:
        return jenni.say('Could not load "find" module.')

    txt = input.group(2)
    parts = txt.split()
    if not parts:
        return jenni.say('Please provide me with a valid nick.')

    nick = parts[0]
    channel = input.sender
    channel = (channel).lower()

    quote_db = find.load_db()
    if quote_db and channel in quote_db and nick in quote_db[channel]:
        quotes_by_nick = quote_db[channel][nick]
    else:
        return jenni.say('There are currently no existing quotes by the provided nick in this channel.')

    quote_by_nick = quotes_by_nick[-1]

    quote = '<%s> %s' % (nick, quote_by_nick)

    write_addquote(quote)

    jenni.say('quote added: %s' % (quote))
grabquote.commands = ['grab']


if __name__ == '__main__':
    print __doc__.strip()

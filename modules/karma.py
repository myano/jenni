#!/usr/bin/python
"""
karma.py - Karma voting module
Copyright 2013
    Patrick Andrew <missionsix@gmail.com>, John Ryan <john@shiftregister.net>

Licensed under the Eiffel Forum License, version 2

1. Permission is hereby granted to use, copy, modify and/or
   distribute this package, provided that:
      * copyright notices are retained unchanged,
      * any distribution of this package, whether modified or not,
        includes this license text.
2. Permission is hereby also granted to distribute binary programs
   which depend on this package. If the binary program depends on a
   modified version of this package, you are encouraged to publicly
   release the modified version of this package.

THIS PACKAGE IS PROVIDED "AS IS" AND WITHOUT WARRANTY. ANY EXPRESS OR
IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
DISCLAIMED. IN NO EVENT SHALL THE AUTHORS BE LIABLE TO ANY PARTY FOR ANY
DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
DAMAGES ARISING IN ANY WAY OUT OF THE USE OF THIS PACKAGE.
"""
import datetime
import operator
import pickle
import re
import time

from os.path import expanduser
from pprint import pprint 

twoseconds = datetime.timedelta(seconds=2)
upvoterate = datetime.timedelta(seconds=30)

# 20 character karma topic, including spaces
KARMA_TOPIC_REGEX = '([\w\s]+){0,20}'

# dict of channel/last person to talk that didn't say +1
LAST_NICK = dict()
HISTORY = dict()

class kdict(dict):

      db_file = expanduse("~/.jenni/karma.pkl")

      def __init__(self):
            print "Loading karma"
            # read python dict back from the file
            try:
                  pkl_file = open(self.db_file, 'rb')
                  self.__dict__  = pickle.load(pkl_file)
                  pkl_file.close()
            except IOError:
                  self.__dict__ = {}

            print '\tKarma DB loaded.'


      def __savekarma(self):
            # write python dict to a file
            output = open(self.db_file, 'wb')
            pickle.dump(self.__dict__, output)
            output.close()


      def __getitem__(self, key):
            try:
                  return self.__dict__[key]
            except KeyError:
                  return 0


      def __setitem__(self, key, value):
            try:
                  self.__dict__[key] += value
            except KeyError:
                  self.__dict__[key] = value

            self.__savekarma()


      def iteritems(self):
            return self.__dict__.iteritems()


KARMADICT = kdict()


def notify(jenni, recipient, text):
    jenni.write(('NOTICE', recipient), text)


def plusplus(jenni, input):

    if input.nick == input.sender:
          notify(jenni, input.nick, "Bite my shiny metal ass!")
          return

    topic = input.group(1)
    name = topic.lstrip().rstrip() if topic else ''
    upvote_time = datetime.datetime.now()

    if name == '' or not name or len(name) == 0:
        name = LAST_NICK.get(input.sender, jenni.nick)
    try:
          last_upvote = HISTORY[input.nick]
          if (upvote_time - last_upvote) < upvoterate and name != input.nick:
                new_upvote = last_upvote + upvoterate
                notify(jenni, input.nick,
                       "You may not upvote until: %s" 
                       % new_upvote.strftime("%H:%M:%S"))
                return
    except KeyError:
          pass

    if name == input.nick:
        print "%s downvoting %s" % (input.nick, name)
        KARMADICT[name] = -1
    else:
        print "%s upvoting %s at %s" %(input.nick, name, 
                                       upvote_time.strftime("%H:%M:%S"))
        KARMADICT[name] = 1

    HISTORY[input.nick] = upvote_time


plusplus.rule = r'.*\+1%s' % KARMA_TOPIC_REGEX
plusplus.priority = 'low'


def minusminus(jenni, input):

    if input.nick == input.sender:
          notify(jenni, input.nick, "Bite my shiny metal ass!")
          return

    topic = input.group(1)
    name = topic.lstrip().rstrip() if topic else ''
    downvote_time = datetime.datetime.now()

    if name == '' or not name or len(name) == 0:
        name = LAST_NICK.get(input.sender, jenni.nick)
    try:
          last_upvote = HISTORY[input.nick]
          if (downvote_time - last_upvote) < upvoterate:
                new_upvote = last_upvote + upvoterate
                notify(jenni, input.nick,
                       "You may not upvote until: %s" 
                       % new_upvote.strftime("%H:%M:%S"))
                return
    except KeyError:
          pass

    print "%s downvoting %s" % (input.nick, name)
    KARMADICT[name] = -1

    HISTORY[input.nick] = downvote_time


minusminus.rule = r'.*-1%s' % KARMA_TOPIC_REGEX
minusminus.priority = 'low'


def askkarma(jenni, input):
    topic = input.group(1)
    name = topic.lstrip().rstrip() if topic else input.nick
    jenni.say("%s is at %d karma." % (name, KARMADICT[name]))


askkarma.rule=r'\.karma%s' % KARMA_TOPIC_REGEX


def karmarank(jenni, input):
    sorted_karma = sorted(KARMADICT.iteritems(), key=operator.itemgetter(1))
    if len(sorted_karma) == 0:
          jenni.say('No karma history')
          return
    losers = sorted_karma[:3]
    winners = sorted_karma[-3:]
    msg1 = ''
    for x in winners:
        msg1="%s:%s   " % (x[0], x[1]) + msg1
    msg1 = "Winners: " + msg1
    msg2 = "Losers: "
    for x in losers:
        msg2+="%s:%s   " % (x[0], x[1])
    jenni.say(msg1)
    time.sleep(0.5)
    jenni.say(msg2)


karmarank.rule=r'\.rank$'


def lastnick(jenni, input):
    if not '+1' in input.group(0):
          if type(input.sender) != None:
                LAST_NICK[input.sender] = input.nick


lastnick.rule = r'.*'


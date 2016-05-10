#!/usr/bin/env python
"""
scores.py - jenni Scores Module
Copyright 2010-2013, Michael Yanovich (yanovich.net) and Matt Meinwald,
    and Samuel Clements

More info:
 * jenni: https://github.com/myano/jenni/
 * Phenny: http://inamidst.com/phenny/
"""

import codecs
from modules import unicode as uc
import pickle
import os
import time


class Scores:
    def __init__(self):
        self.scores_filename = os.path.expanduser('~/.jenni/scores.txt')
        self.scores_dict = dict()
        self.load()
        self.STRINGS = {
            "nochan": "Channel, {0}, has no users with scores.",
            "nouser": "{0} has no score in {1}.",
            "rmuser": "User, {0}, has been removed from room: {1}.",
            "cantadd": "I'm sorry, but I'm afraid I can't add that user!",
            "denied": "I'm sorry, but I can't let you do that!",
            "invalid": "Invalid parameters entered.",
        }

    def str_score(self, nick, channel):
        return "%s: +%s/-%s, %s" % (nick,
                                    self.scores_dict[channel][nick][0],
                                    self.scores_dict[channel][nick][1],
                                    self.scores_dict[channel][nick][0] -
                                    self.scores_dict[channel][nick][1])

    def editpoints(self, jenni, input, nick, points):
        if not nick:
            return
        nick = uc.encode(nick.lower())
        if not nick:
            jenni.reply(self.STRINGS["cantadd"])
        elif (not input.admin) and (input.nick).lower() == nick:
            jenni.reply(self.STRINGS["denied"])
        else:
            nick = nick.lower()
            chan = (input.sender).lower()
            if chan not in self.scores_dict:
                self.scores_dict[chan] = {}
            if not nick in self.scores_dict[chan]:
                self.scores_dict[chan][nick] = [0, 0]

            # Add a point if points is TRUE, remove if FALSE
            if points:
                self.scores_dict[chan][nick][0] += 1
            else:
                self.scores_dict[chan][nick][1] += 1

            self.save()
            jenni.say(self.str_score(nick, chan))

    def save(self):
        """ Save to file in comma seperated values """
        os.rename(self.scores_filename, '%s-%s' % (self.scores_filename, str(time.time())))
        scores_file = codecs.open(self.scores_filename, 'w', encoding='utf-8')
        for each_chan in self.scores_dict:
            for each_nick in self.scores_dict[each_chan]:
                line = '{0},{1},{2},{3}\n'.format(each_chan, each_nick, self.scores_dict[each_chan][each_nick][0], self.scores_dict[each_chan][each_nick][1])
                scores_file.write(uc.decode(line))
        scores_file.close()

    def load(self):
        try:
            sfile = open(self.scores_filename, 'r')
        except:
            sfile = open(self.scores_filename, 'w')
            sfile.close()
            return
        for line in sfile:
            values = line.split(',')
            if len(values) == 4:
                channel = (values[0]).lower()
                if channel not in self.scores_dict:
                    self.scores_dict[channel] = dict()
                self.scores_dict[channel][values[1]] = [int(values[2]),
                                                          int(values[3])]
        if not self.scores_dict:
            self.scores_dict = dict()
        sfile.close()

    def view_scores(self, jenni, input):

        def ten(channel, ranking):
            channel = channel.lower()
            if channel not in self.scores_dict:
                return self.STRINGS["nochan"].format(channel)
            q = 0
            top_scores = list()
            if ranking == 'b':
                tob = 'Bottom'
            elif ranking == 't':
                tob= 'Top'
            str_say = "\x02%s 10 (for %s):\x02" % (tob, channel)
            sort = True
            if ranking == 'b':
                sort = False
            scores = sorted(self.scores_dict[channel].iteritems(),
                            key=lambda (k, v): (v[0] - v[1]), reverse=sort)
            for key, value in scores:
                top_scores.append(self.str_score(key, channel))
                if len(scores) == q + 1:
                    str_say += ' %s' % (uc.decode(top_scores[q]))
                else:
                    str_say += ' %s |' % (uc.decode(top_scores[q]))
                q += 1
                if q > 9:
                    break
            return str_say

        def given_user(nick, channel):
            nick = uc.encode(nick.lower())
            channel = channel.lower()
            if channel in self.scores_dict:
                if nick in self.scores_dict[channel]:
                    return self.str_score(nick, channel)
                else:
                    return self.STRINGS["nouser"].format(nick, channel)
            else:
                return self.STRINGS["nochan"].format(channel)

        self.load()
        line = input.group()[7:].split()
        current_channel = input.sender
        current_channel = current_channel.lower()


        if len(line) == 0 or (len(line) == 1 and line[0] == 'top'):
            ## .scores
            t10 = ten(current_channel, 't')
            jenni.say(t10)


        elif len(line) == 2 and (not line[0].startswith("#")) and line[1].startswith("#") and line[0] == "bottom":
            ## .scores bottom <channel>
            b10 = ten(line[1], 'b')
            jenni.say(b10)

        elif len(line) == 1 and not line[0].startswith("#"):
            ## .scores <nick>
            jenni.say(given_user(line[0], current_channel))

        elif len(line) == 1 and line[0].startswith("#"):
            ## .scores <channel>
            t10_chan = ten(line[0], 't')
            jenni.say(t10_chan)

        elif len(line) == 2 and line[0].startswith("#") and line[1] != "all":
            ## .scores <channel> <nick>
            jenni.say(given_user(line[1], line[0]))

        elif len(line) == 2:
            ## .scores <nick> all
            outstr = "Scores for {0} in: ".format(line[0])
            for channel in self.scores_dict:
                for nick in self.scores_dict[channel]:
                    if nick == line[0].lower():
                        nick_scores = self.scores_dict[channel][nick]
                        outstr += "{0}: {1}/{2}, {3} | ".format(channel,
                                                                nick_scores[0],
                                                                nick_scores[1],
                                                                int(
                                                                nick_scores[0]
                                                                ) - int(
                                                                nick_scores[1]
                                                                ))
            if outstr.endswith("| "):
                outstr = outstr[:-2]
            jenni.say(outstr)

    def setpoint(self, jenni, input, line):
        if not input.admin:
            return
        line = line[10:].split()
        if len(line) != 4:
            return
        channel = uc.encode(line[0]).lower()
        nick = uc.encode(line[1]).lower()
        try:
            add = int(line[2])
            sub = int(line[3])
        except:
            jenni.say(self.STRINGS["invalid"])
            return

        if add < 0 or sub < 0:
            jenni.reply("You are doing it wrong.")
            return

        if channel not in self.scores_dict:
            self.scores_dict[channel] = dict()

        self.scores_dict[channel][nick] = [int(add), int(sub)]
        self.save()
        jenni.say(self.str_score(nick, channel))

    def rmuser(self, jenni, input, line):
        if not input.admin:
            return
        if len(line) < 9:
            jenni.reply("No input provided.")
            return
        line = line[8:].split()
        channel = uc.encode((input.sender).lower())
        nick = uc.encode(line[0]).lower()

        def check(nick, channel):
            nick = nick.lower()
            channel = channel.lower()
            if channel in self.scores_dict:
                if nick in self.scores_dict[channel]:
                    del self.scores_dict[channel][nick]
                    return self.STRINGS["rmuser"].format(nick, channel)
                else:
                    return self.STRINGS["nouser"].format(nick, channel)
            else:
                return self.STRINGS["nochan"].format(channel)

        if len(line) == 1:
            ## .rmuser <nick>
            result = check(nick, (input.sender).lower())
            self.save()
        elif len(line) == 2:
            ## .rumser <channel> <nick>
            result = check(line[1], nick)
            self.save()

        jenni.say(result)

# jenni commands
scores = Scores()


def addpoint_command(jenni, input):
    """.addpoint <nick> - Adds 1 point to the score system for <nick>."""
    nick = input.group(2)
    if nick:
        nick = nick.strip().split()[0]
    scores.editpoints(jenni, input, nick, True)
addpoint_command.commands = ['addpoint']
addpoint_command.priorty = 'high'
addpoint_command.rate = 60 * 10


def second_addpoint_command(jenni, input):
    """<nick>++ - Adds 1 point to the score system for <nick>."""
    nick = input.group(1)
    if nick:
        nick = nick.strip()
    if len(nick) == list(nick).count('+'):
        return
    scores.editpoints(jenni, input, nick, True)
second_addpoint_command.rule = r'^(\S+)\+\+($|\s)'
second_addpoint_command.priority = 'high'
second_addpoint_command.rate = 60 * 10


def rmpoint_command(jenni, input):
    """.rmpoint <nick> - Removes 1 point to the score system for <nick>."""
    nick = input.group(2)
    if nick:
        nick = nick.strip().split()[0]
    scores.editpoints(jenni, input, nick, False)
rmpoint_command.commands = ['rmpoint']
rmpoint_command.priority = 'high'
rmpoint_command.rate = 60 * 10


def second_rmpoint_command(jenni, input):
    """<nick>-- - Removes 1 point to the score system for <nick>."""
    nick = input.group(1)
    if nick:
        nick = nick.strip()
    if len(nick) == list(nick).count('-'):
        return
    scores.editpoints(jenni, input, nick, False)
second_rmpoint_command.rule = r'^(\S+)\-\-($|\s)'
second_rmpoint_command.priority = 'high'
second_rmpoint_command.rate = 60 * 10


def view_scores(jenni, input):
    """.scores <channel> <user> - Lists all users and their point values in the system. channel and user parameters are optional"""
    scores.view_scores(jenni, input)
view_scores.commands = ['points', 'point', 'scores', 'score']
view_scores.priority = 'medium'
view_scores.rate = 60 * 3


def setpoint(jenni, input):
    """.setpoint <channel> <nick> <number> <number> - Sets score for user."""
    line = input.group()
    if line:
        line = line.lstrip().rstrip()
    scores.setpoint(jenni, input, line)
setpoint.commands = ['setpoint', 'setscore']
setpoint.priority = 'medium'


def removeuser(jenni, input):
    """.rmuser <nick> -- Removes a given user from the system."""
    line = input.group()
    if line:
        line = line.lstrip().rstrip()
    scores.rmuser(jenni, input, line)
removeuser.commands = ['rmuser']
removeuser.priority = 'medium'


if __name__ == '__main__':
    print __doc__.strip()

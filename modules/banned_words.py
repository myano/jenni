#!/usr/bin/env python
"""
banned_words.py - jenni banned words module
Copyright 2015, Josh Begleiter (jbegleiter.com)
Licensed under the Eiffel Forum License 2.

More info:
 * jenni: https://github.com/myano/jenni/
 * Phenny: http://inamidst.com/phenny/
"""

import imp, os, re, time

WARNINGS_TABLE = 'banned_words_warnings'
warnings_initialized = False
current_warnings = {}

def ban_user(jenni, full_ident, channel, bad_nick):
    mask = full_ident
    reason = "You have violated the banned word policy."
    jenni.write(['MODE', channel, '+b', mask])
    jenni.write(['KICK', channel, bad_nick, ' :{0}'.format(reason)])

    # Reset the warnings
    try:
        del_warning(jenni, channel, bad_nick)
    except:
        pass

def add_warning(jenni, channel, bad_nick, new_num_warnings):
    global current_warnings

    # If this is the first time we've warned the user
    if new_num_warnings == 1:
        current_warnings[channel][bad_nick] = 1
    else:
        current_warnings[channel][bad_nick] += 1

    if jenni.db_layer.db_capable:
        # Insert instead of update
        if new_num_warnings == 1:
            args = {
                'nick': bad_nick,
                'channel': channel,
                'num_warnings': 1,
            }

            jenni.db_layer.insert_row(WARNINGS_TABLE, args)
        else:
            updates = {
                'num_warnings': current_warnings[channel][bad_nick],
            }

            conditions = {
                'channel': channel,
                'nick': bad_nick,
            }

            jenni.db_layer.update_row(WARNINGS_TABLE, updates, conditions)

def del_warning(jenni, channel, bad_nick):
    global current_warnings

    del current_warnings[channel][bad_nick]

    if jenni.db_layer.db_capable:
        args = {
            'channel': channel,
            'nick': bad_nick,
        }

        jenni.db_layer.delete_rows(WARNINGS_TABLE, args)

def initialize_warnings(jenni):
    global WARNINGS_TABLE
    global warnings_initialized
    global current_warnings

    if warnings_initialized is False:
        if jenni.db_layer.db_capable:
            # We may need to initialize this table
            if jenni.db_layer.check_table_exists(WARNINGS_TABLE):
                # Get the current warnings
                col_order = ['nick', 'channel', 'num_warnings']
                # Use 1=1 to get all rows to ensure order
                for row in jenni.db_layer.get_all_rows(WARNINGS_TABLE, col_order):
                    nick, channel, num_warnings = row
                    if channel not in current_warnings:
                        current_warnings[channel] = {}
                    current_warnings[channel][nick] = num_warnings
            else:
                # This should have gotten run as part of migrations (see jenni_home/migrations)
                table_cols = {
                    'nick': 'VARCHAR(255)',
                    'channel': 'VARCHAR(255)',
                    'num_warnings': 'INT',
                }

                # Create table
                jenni.db_layer.create_table(WARNINGS_TABLE, table_cols)
        warnings_initialized = True

def is_unbannable(jenni, channel, bad_nick):
    chan_ops = []
    chan_hops = []
    chan_voices = []
    if channel in jenni.ops:
        chan_ops = jenni.ops[channel]

    if channel in jenni.hops:
        chan_hops = jenni.hops[channel]

    if channel in jenni.voices:
        chan_voices = jenni.voices[channel]

    # First ensure jenni is an op
    if jenni.nick not in chan_ops:
        return True

    # Next ensure the sender isn't op, half-op, or voice
    return (bad_nick in chan_ops or bad_nick in chan_hops or bad_nick in chan_voices)

def banned_words(jenni, input):
    """
    Listens to a channel for bad words. If one is found it first
    warns a user, then after X warnings kickbans them, where
    X defaults to 0, meaning instant ban.

    User warnings are stored in memory if there's no database driver,
    otherwise it's stored in Jenni's sqlite database. This means that
    when no database is present the warnings will not persist across
    Jenni's reboots.

    Currently bad words must be added to the config, as a future
    addition bad words will be editable by admins using a command.
    """
    global current_warnings

    if not hasattr(jenni.config, 'bad_word_limit') or not hasattr(jenni.config, 'bad_words'):
        return

    initialize_warnings(jenni)

    bad_word_limit = jenni.config.bad_word_limit or 0
    bad_words = jenni.config.bad_words or {}

    if len(bad_words) == 0:
        return

    # We only want to execute in a channel for which we have a wordlist
    if not input.sender.startswith("#") or input.sender not in bad_words:
        return

    # Find which word triggered the event
    # Get a unique list of bad words
    if input.sender not in bad_words:
        return

    match_word = False
    words = bad_words[input.sender]
    for word in words:
        if re.match(r'.*(?:%s).*' % word, input.group()):
            match_word = True
            break

    # Wrong channel for the match
    if not match_word:
        return

    # We don't want to warn or kickban admins
    if input.admin:
        return

    channel = input.sender
    bad_nick = input.nick

    # Next ensure the sender isn't op, half-op, or voice
    # and that Jenni is an op herself
    if is_unbannable(jenni, channel, bad_nick):
        return

    if channel not in current_warnings:
        current_warnings[channel] = {}

    full_ident = input.full_ident
    if bad_word_limit == 0:
        ban_user(jenni, full_ident, channel, bad_nick)
    elif bad_nick in current_warnings[channel]:
        if current_warnings[channel][bad_nick] >= bad_word_limit:
            ban_user(jenni, full_ident, channel, bad_nick)
        else:
            add_warning(jenni, channel, bad_nick, current_warnings[channel][bad_nick] + 1)
            jenni.say(bad_word_warning(bad_nick, bad_word_limit, current_warnings[channel][bad_nick]))
    else:
        add_warning(jenni, channel, bad_nick, 1)
        jenni.say(bad_word_warning(bad_nick, bad_word_limit, 1))
banned_words.rule = r'(.*)'
banned_words.priority = 'high'

def list_banned_words(jenni, input):
    # Only executable in channel
    if not input.sender.startswith('#'):
        return

    if input.sender not in jenni.config.bad_words:
        jenni.say('There are no banned words in this channel.')
    else:
        chan_words = ', '.join(jenni.config.bad_words[input.sender])
        jenni.say('Banned words: {0}'.format(chan_words))
list_banned_words.commands = ["list_banned_words"]
list_banned_words.example = '.list_banned_words'
list_banned_words.priority = 'low'

# Create the warning message for violation of this policy
def bad_word_warning(nick, bad_word_limit, current_warnings):
    base_warning = "{0}: Please refrain from using that word or phrase. ".format(nick)
    warnings_remaining = bad_word_limit - current_warnings
    if warnings_remaining == 0:
      base_warning += "You will be banned the next time you violate this policy."
    else:
      base_warning += "You will be banned after {0} further violations of this policy.".format(warnings_remaining + 1)

    return base_warning

if __name__ == '__main__':
    print __doc__.strip()


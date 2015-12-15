#!/usr/bin/env python
'''
admin.py - jenni Admin Module
Copyright 2010-2013, Sean B. Palmer (inamidst.com) and Michael Yanovich (yanovich.net)
Licensed under the Eiffel Forum License 2.

More info:
 * jenni: https://github.com/myano/jenni/
 * Phenny: http://inamidst.com/phenny/
'''

import os
import time

intentional_part = False

def reload_confs(jenni, input):
    # Reload known configs. This is an owner-only command.
    if not input.owner: return

    config_modules = []

    jenni.config.config_helper.load_modules(config_modules)
    jenni.reply("Reloaded configs")
reload_confs.commands = ['reload_configs', 'reload_config', 'reload_conf']
reload_confs.priority = 'low'

def join(jenni, input):
    '''Join the specified channel. This is an owner-only command.'''
    # Can only be done in privmsg by an owner
    if input.sender.startswith('#'): return
    if not input.owner:
        return jenni.say('You do not have owner privs.')
    incoming = input.group(2)
    if not incoming:
        return jenni.say('Please provide some channels to join.')
    inc = incoming.split(' ')
    if len(inc) > 2:
        ## 3 or more inputs
        return jenni.say('Too many inputs.')
    if input.owner:
        channel = inc[0]
        key = str()
        if len(inc) > 1:
            ## 2 inputs
            key = inc[1]
        if not key:
            jenni.write(['JOIN'], channel)
        else: jenni.write(['JOIN', channel, key])
join.commands = ['join']
join.priority = 'low'
join.example = '.join #example or .join #example key'

def part(jenni, input):
    '''Part the specified channel. This is an admin-only command.'''
    # Can only be done in privmsg by an admin
    global intentional_part
    if input.sender.startswith('#'): return
    if input.admin:
        intentional_part = True
        jenni.write(['PART'], input.group(2))
part.commands = ['part']
part.priority = 'low'
part.example = '.part #example'

def quit(jenni, input):
    '''Quit from the server. This is an owner-only command.'''
    # Can only be done in privmsg by the owner
    if input.sender.startswith('#'): return
    if input.owner:
        jenni.write(['QUIT'])
        __import__('os')._exit(0)
quit.commands = ['quit']
quit.priority = 'low'

def msg(jenni, input):
    # Can only be done in privmsg by an admin
    if input.sender.startswith('#'): return
    a, b = input.group(2), input.group(3)
    if (not a) or (not b): return
    if (a.startswith('+') or a.startswith('@')) and not input.owner:
        return
    al = a.lower()
    parts = al.split(',')
    if not input.owner:
        notallowed = ['chanserv', 'nickserv', 'hostserv', 'memoserv', 'saslserv', 'operserv']
        #if al == 'chanserv' or al == 'nickserv' or al == 'hostserv' or al == 'memoserv' or al == 'saslserv' or al == 'operserv':
        for each in notallowed:
            for part in parts:
                if part in notallowed:
                    return
    helper = False
    if hasattr(jenni.config, 'helpers'):
        if a in jenni.config.helpers and (input.host in jenni.config.helpers[a] or (input.nick).lower() in jenni.config.helpers[a]):
            helper = True
    if input.admin or helper:
        for part in parts:
            jenni.msg(part, b)
msg.rule = (['msg'], r'(#?\S+) (.+)')
msg.priority = 'low'

def me(jenni, input):
    # Can only be done in privmsg by an admin
    if input.sender.startswith('#'): return
    a, b = input.group(2), input.group(3)
    helper = False
    if hasattr(jenni.config, 'helpers'):
        if a in jenni.config.helpers and (input.host in jenni.config.helpers[a] or (input.nick).lower() in jenni.config.helpers[a]):
            helper = True
    if input.admin or helper:
        if a and b:
            msg = '\x01ACTION %s\x01' % input.group(3)
            jenni.msg(input.group(2), msg, x=True)
me.rule = (['me'], r'(#?\S+) (.*)')
me.priority = 'low'


def defend_ground(jenni, input):
    '''
    This function monitors all kicks across all channels jenni is in. If she
    detects that she is the one kicked she'll automatically join that channel.

    WARNING: This may not be needed and could cause problems if jenni becomes
    annoying. Please use this with caution.
    '''
    channel = input.sender
    jenni.write(['JOIN'], channel)
    time.sleep(10)
    jenni.write(['JOIN'], channel)
defend_ground.event = 'KICK'
defend_ground.rule = '.*'
defend_ground.priority = 'low'


def defend_ground2(jenni, input):
    global intentional_part
    if not intentional_part and input.nick == jenni.config.nick:
        intentional_part = False
        channel = input.sender
        jenni.write(['JOIN'], channel)
        time.sleep(10)
        jenni.write(['JOIN'], channel)
defend_ground2.event = 'PART'
defend_ground2.rule = '.*'
defend_ground2.priority = 'low'


def blocks(jenni, input):
    if not input.admin: return

    if hasattr(jenni.config, 'logchan_pm') and input.sender != jenni.config.logchan_pm:
        # BLOCKS USED - user in ##channel - text
        jenni.msg(jenni.config.logchan_pm, 'BLOCKS USED - %s in %s -- %s' % (input.nick, input.sender, input))

    STRINGS = {
            'success_del' : 'Successfully deleted block: %s',
            'success_add' : 'Successfully added block: %s',
            'no_nick' : 'No matching nick block found for: %s',
            'no_host' : 'No matching hostmask block found for: %s',
            'invalid' : 'Invalid format for %s a block. Try: .blocks add (nick|hostmask) jenni',
            'invalid_display' : 'Invalid input for displaying blocks.',
            'nonelisted' : 'No %s listed in the blocklist.',
            'huh' : 'I could not figure out what you wanted to do.',
            }

    if not os.path.isfile('blocks'):
        blocks = open('blocks', 'w')
        blocks.write('\n')
        blocks.close()

    blocks = open('blocks', 'r')
    contents = blocks.readlines()
    blocks.close()

    try: masks = contents[0].replace('\n', '').split(',')
    except: masks = ['']

    try: nicks = contents[1].replace('\n', '').split(',')
    except: nicks = ['']

    text = input.group().split()

    if len(text) == 3 and text[1] == 'list':
        if text[2] == 'hostmask':
            if len(masks) > 0 and masks.count('') == 0:
                for each in masks:
                    if len(each) > 0:
                        jenni.say('blocked hostmask: ' + each)
            else:
                jenni.reply(STRINGS['nonelisted'] % ('hostmasks'))
        elif text[2] == 'nick':
            if len(nicks) > 0 and nicks.count('') == 0:
                for each in nicks:
                    if len(each) > 0:
                        jenni.say('blocked nick: ' + each)
            else:
                jenni.reply(STRINGS['nonelisted'] % ('nicks'))
        else:
            jenni.reply(STRINGS['invalid_display'])

    elif len(text) == 4 and text[1] == 'add':
        if text[2] == 'nick':
            nicks.append(text[3])
        elif text[2] == 'hostmask':
            masks.append(text[3])
        else:
            jenni.reply(STRINGS['invalid'] % ('adding'))
            return

        jenni.reply(STRINGS['success_add'] % (text[3]))

    elif len(text) == 4 and text[1] == 'del':
        if text[2] == 'nick':
            try:
                nicks.remove(text[3])
                jenni.reply(STRINGS['success_del'] % (text[3]))
            except:
                jenni.reply(STRINGS['no_nick'] % (text[3]))
                return
        elif text[2] == 'hostmask':
            try:
                masks.remove(text[3])
                jenni.reply(STRINGS['success_del'] % (text[3]))
            except:
                jenni.reply(STRINGS['no_host'] % (text[3]))
                return
        else:
            jenni.reply(STRINGS['invalid'] % ('deleting'))
            return
    else:
        jenni.reply(STRINGS['huh'])

    os.remove('blocks')
    blocks = open('blocks', 'w')
    masks_str = ','.join(masks)
    if len(masks_str) > 0 and ',' == masks_str[0]:
        masks_str = masks_str[1:]
    blocks.write(masks_str)
    blocks.write('\n')
    nicks_str = ','.join(nicks)
    if len(nicks_str) > 0 and ',' == nicks_str[0]:
        nicks_str = nicks_str[1:]
    blocks.write(nicks_str)
    blocks.close()

blocks.commands = ['blocks']
blocks.priority = 'low'
blocks.thread = False

char_replace = {
        r'\x01': chr(1),
        r'\x02': chr(2),
        r'\x03': chr(3),
        }

def write_raw(jenni, input):
    if not input.owner: return
    txt = input.bytes[7:]
    txt = txt.encode('utf-8')
    a = txt.split(':')
    status = False
    if len(a) > 1:
        newstr = u':'.join(a[1:])
        for x in char_replace:
            if x in newstr:
                newstr = newstr.replace(x, char_replace[x])
        jenni.write(a[0].split(), newstr, raw=True)
        status = True
    elif a:
        b = a[0].split()
        jenni.write([b[0].strip()], u' '.join(b[1:]), raw=True)
        status = True
    if status:
        jenni.say('Message sent to server.')
write_raw.commands = ['write']
write_raw.priority = 'high'
write_raw.thread = False

if __name__ == '__main__':
    print __doc__.strip()


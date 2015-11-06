#!/usr/bin/env python
"""
bot.py - jenni IRC Bot
Copyright 2009-2013, Michael Yanovich (yanovich.net)
Copyright 2008-2013, Sean B. Palmer (inamidst.com)
Licensed under the Eiffel Forum License 2.

More info:
 * jenni: https://github.com/myano/jenni/
 * Phenny: http://inamidst.com/phenny/
"""

import time, sys, os, re, threading, imp
import irc

home = os.getcwd()

def decode(bytes):
    try: text = bytes.decode('utf-8')
    except UnicodeDecodeError:
        try: text = bytes.decode('iso-8859-1')
        except UnicodeDecodeError:
            text = bytes.decode('cp1252')
    return text

class Jenni(irc.Bot):
    def __init__(self, config):
        lc_pm = None
        if hasattr(config, "logchan_pm"): lc_pm = config.logchan_pm
        logging = False
        if hasattr(config, "logging"): logging = config.logging
        ipv6 = False
        if hasattr(config, 'ipv6'): ipv6 = config.ipv6
        serverpass = None
        if hasattr(config, 'serverpass'): serverpass = config.serverpass
        user = None
        if hasattr(config, 'user'): user = config.user
        args = (config.nick, config.name, config.channels, user, serverpass, lc_pm, logging, ipv6)
        ## next, try putting a try/except around the following line
        irc.Bot.__init__(self, *args)
        self.config = config
        self.doc = {}
        self.stats = {}
        self.times = {}
        self.excludes = {}
        if hasattr(config, 'excludes'):
            self.excludes = config.excludes
        self.setup()

    def setup(self):
        self.variables = {}

        filenames = []

        # Default module folder + extra folders
        module_folders = [os.path.join(home, 'modules')]
        module_folders.extend(getattr(self.config, 'extra', []))

        excluded = getattr(self.config, 'exclude', [])
        enabled = getattr(self.config, 'enable', [])

        for folder in module_folders:
            if os.path.isfile(folder):
                filenames.append(folder)
            elif os.path.isdir(folder):
                for fn in os.listdir(folder):
                    if fn.endswith('.py') and not fn.startswith('_'):
                        name = os.path.basename(fn)[:-3]
                        # If whitelist is present only include whitelisted
                        # Never include blacklisted items
                        if name in enabled or not enabled and name not in excluded:
                            filenames.append(os.path.join(folder, fn))

        modules = []
        for filename in filenames:
            name = os.path.basename(filename)[:-3]
            # if name in sys.modules:
            #     del sys.modules[name]
            try: module = imp.load_source(name, filename)
            except Exception, e:
                print >> sys.stderr, "Error loading %s: %s (in bot.py)" % (name, e)
            else:
                if hasattr(module, 'setup'):
                    module.setup(self)
                self.register(vars(module))
                modules.append(name)

        if modules:
            print >> sys.stderr, 'Registered modules:', ', '.join(sorted(modules))
        else:
            print >> sys.stderr, "Warning: Couldn't find any modules"

        self.bind_commands()

    def register(self, variables):
        # This is used by reload.py, hence it being methodised
        for name, obj in variables.iteritems():
            if hasattr(obj, 'commands') or hasattr(obj, 'rule'):
                self.variables[name] = obj

    def bind_commands(self):
        self.commands = {'high': {}, 'medium': {}, 'low': {}}

        def bind(self, priority, regexp, func):
            # register documentation
            if not hasattr(func, 'name'):
                func.name = func.__name__
            if func.__doc__:
                if hasattr(func, 'example'):
                    example = func.example
                    example = example.replace('$nickname', self.nick)
                else: example = None
                self.doc[func.name] = (func.__doc__, example)
            self.commands[priority].setdefault(regexp, []).append(func)
            regexp = re.sub('\x01|\x02', '', regexp.pattern)
            return (func.__module__, func.__name__, regexp, priority)

        def sub(pattern, self=self):
            # These replacements have significant order
            pattern = pattern.replace('$nickname', re.escape(self.nick))
            return pattern.replace('$nick', r'%s[,:] +' % re.escape(self.nick))

        bound_funcs = []
        for name, func in self.variables.iteritems():
            # print name, func
            if not hasattr(func, 'priority'):
                func.priority = 'medium'

            if not hasattr(func, 'thread'):
                func.thread = True

            if not hasattr(func, 'event'):
                func.event = 'PRIVMSG'
            else:
                if func.event:
                    func.event = func.event.upper()
                else:
                    continue

            if not hasattr(func, 'rate'):
                if hasattr(func, 'commands'):
                    func.rate = 3
                else:
                    func.rate = -1

            if hasattr(func, 'rule'):
                if isinstance(func.rule, str):
                    pattern = sub(func.rule)
                    regexp = re.compile(pattern)
                    bound_funcs.append(bind(self, func.priority, regexp, func))

                if isinstance(func.rule, tuple):
                    # 1) e.g. ('$nick', '(.*)')
                    if len(func.rule) == 2 and isinstance(func.rule[0], str):
                        prefix, pattern = func.rule
                        prefix = sub(prefix)
                        regexp = re.compile(prefix + pattern)
                        bound_funcs.append(bind(self, func.priority, regexp, func))

                    # 2) e.g. (['p', 'q'], '(.*)')
                    elif len(func.rule) == 2 and isinstance(func.rule[0], list):
                        prefix = self.config.prefix
                        commands, pattern = func.rule
                        for command in commands:
                            command = r'(?i)(%s)\b(?: +(?:%s))?' % (command, pattern)
                            regexp = re.compile(prefix + command)
                            bound_funcs.append(bind(self, func.priority, regexp, func))

                    # 3) e.g. ('$nick', ['p', 'q'], '(.*)')
                    elif len(func.rule) == 3:
                        prefix, commands, pattern = func.rule
                        prefix = sub(prefix)
                        for command in commands:
                            command = r'(?i)(%s) +' % command
                            regexp = re.compile(prefix + command + pattern)
                            bound_funcs.append(bind(self, func.priority, regexp, func))

            if hasattr(func, 'commands'):
                for command in func.commands:
                    template = r'(?i)^%s(%s)(?: +(.*))?$'
                    pattern = template % (self.config.prefix, command)
                    regexp = re.compile(pattern)
                    bound_funcs.append(bind(self, func.priority, regexp, func))

        max_pattern_width = max(len(f[2]) for f in bound_funcs)
        for module, name, regexp, priority in sorted(bound_funcs):
            encoded_regex = regexp.encode('utf-8').ljust(max_pattern_width)
            print ('{0} | {1}.{2}, {3} priority'.format(encoded_regex,  module, name, priority))

    def wrapped(self, origin, text, match):
        class JenniWrapper(object):
            def __init__(self, jenni):
                self._bot = jenni

            def __getattr__(self, attr):
                sender = origin.sender or text
                if attr == 'reply':
                    return (lambda msg:
                        self._bot.msg(sender, origin.nick + ': ' + msg))
                elif attr == 'say':
                    return lambda msg: self._bot.msg(sender, msg)
                elif attr == 'bot':
                    # Allow deprecated usage of jenni.bot.foo but print a warning to the console
                    print "Warning: Direct access to jenni.bot.foo is deprecated.  Please use jenni.foo instead."
                    import traceback
                    traceback.print_stack()
                    # Let this keep working by passing it transparently to _bot
                    return self._bot
                return getattr(self._bot, attr)

            def __setattr__(self, attr, value):
                if attr in ('_bot',):
                    # Explicitly allow the wrapped class to be set during __init__()
                    return super(JenniWrapper, self).__setattr__(attr, value)
                else:
                    # All other attributes will be set on the wrapped class transparently
                    return setattr(self._bot, attr, value)

        return JenniWrapper(self)

    def input(self, origin, text, bytes, match, event, args):
        class CommandInput(unicode):
            def __new__(cls, text, origin, bytes, match, event, args):
                s = unicode.__new__(cls, text)
                s.sender = origin.sender
                s.nick = origin.nick
                s.event = event
                s.bytes = bytes
                s.match = match
                s.group = match.group
                s.groups = match.groups
                s.ident = origin.user
                s.raw = origin
                s.args = args
                s.mode = origin.mode
                s.mode_target = origin.mode_target
                s.names = origin.names
                s.full_ident = origin.full_ident
                s.admin = origin.nick in self.config.admins
                if s.admin == False:
                    for each_admin in self.config.admins:
                        re_admin = re.compile(each_admin)
                        if re_admin.findall(origin.host):
                            s.admin = True
                        elif '@' in each_admin:
                            temp = each_admin.split('@')
                            re_host = re.compile(temp[1])
                            if re_host.findall(origin.host):
                                s.admin = True
                s.owner = origin.nick + '@' + origin.host == self.config.owner
                if s.owner == False: s.owner = origin.nick == self.config.owner
                s.host = origin.host
                return s

        return CommandInput(text, origin, bytes, match, event, args)

    def call(self, func, origin, jenni, input):
        nick = (input.nick).lower()

        ## rate limiting
        if nick in self.times:
            if func in self.times[nick]:
                if not input.admin:
                    ## admins are not rate limited
                    if time.time() - self.times[nick][func] < func.rate:
                        self.times[nick][func] = time.time()
                        return
        else:
            self.times[nick] = dict()

        self.times[nick][func] = time.time()

        try:
            if hasattr(self, 'excludes'):
                if (input.sender).lower() in self.excludes:
                    if '!' in self.excludes[(input.sender).lower()]:
                        # block all function calls for this channel
                        return
                    fname = func.func_code.co_filename.split('/')[-1].split('.')[0]
                    if fname in self.excludes[(input.sender).lower()]:
                        # block function call if channel is blacklisted
                        return
        except Exception, e:
            print "Error attempting to block:", str(func.name)
            self.error(origin)

        try:
            func(jenni, input)
        except Exception, e:
            self.error(origin)

    def limit(self, origin, func):
        if origin.sender and origin.sender.startswith('#'):
            if hasattr(self.config, 'limit'):
                limits = self.config.limit.get(origin.sender)
                if limits and (func.__module__ not in limits):
                    return True
        return False

    def dispatch(self, origin, args):
        bytes, event, args = args[0], args[1], args[2:]
        text = decode(bytes)

        for priority in ('high', 'medium', 'low'):
            items = self.commands[priority].items()
            for regexp, funcs in items:
                for func in funcs:
                    if event != func.event: continue

                    match = regexp.match(text)
                    if match:
                        if self.limit(origin, func): continue

                        jenni = self.wrapped(origin, text, match)
                        input = self.input(origin, text, bytes, match, event, args)

                        nick = (input.nick).lower()

                        # blocking ability
                        if os.path.isfile("blocks"):
                            g = open("blocks", "r")
                            contents = g.readlines()
                            g.close()

                            try: bad_masks = contents[0].split(',')
                            except: bad_masks = ['']

                            try: bad_nicks = contents[1].split(',')
                            except: bad_nicks = ['']

                            # check for blocked hostmasks
                            if len(bad_masks) > 0:
                                host = origin.host
                                host = host.lower()
                                for hostmask in bad_masks:
                                    hostmask = hostmask.replace("\n", "").strip()
                                    if len(hostmask) < 1: continue
                                    try:
                                        re_temp = re.compile(hostmask)
                                        if re_temp.findall(host):
                                            return
                                    except:
                                        if hostmask in host:
                                            return
                            # check for blocked nicks
                            if len(bad_nicks) > 0:
                                for nick in bad_nicks:
                                    nick = nick.replace("\n", "").strip()
                                    if len(nick) < 1: continue
                                    try:
                                        re_temp = re.compile(nick)
                                        if re_temp.findall(input.nick):
                                            return
                                    except:
                                        if nick in input.nick:
                                            return
                        # stats
                        if func.thread:
                            targs = (func, origin, jenni, input)
                            t = threading.Thread(target=self.call, args=targs)
                            t.start()
                        else: self.call(func, origin, jenni, input)

                        for source in [origin.sender, origin.nick]:
                            try: self.stats[(func.name, source)] += 1
                            except KeyError:
                                self.stats[(func.name, source)] = 1

if __name__ == '__main__':
    print __doc__


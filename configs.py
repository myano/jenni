#!/usr/bin/env python
"""
configs.py - jenni IRC bot config manager
Copyright 2014-2016, Josh Begleiter (jbegleiter).com
Copyright 2009-2016, Michael Yanovich (yanovich.net)
Copyright 2008-2013, Sean B. Palmer (inamidst.com)
Licensed under the Eiffel Forum License 2.

This is invoked in the jenni starter to store the
config helper in jenni.config

More info:
 * jenni: https://github.com/myano/jenni/
 * Phenny: http://inamidst.com/phenny/
"""

import imp, os, sys

class Configs():
    def __init__(self, config_paths):
        self.config_paths = config_paths

    def load_modules(self, config_modules):
        for config_name in self.config_paths:
            # Ensure we take the basename, even if the file includes periods
            name = os.path.basename(config_name).split('.')[0] + '_config'
            module = imp.load_source(name, config_name)
            module.filename = config_name

            if not hasattr(module, 'prefix'):
                module.prefix = r'\.'

            if not hasattr(module, 'name'):
                module.name = 'jenni yanosbot, https://git.io/jenni'

            if not hasattr(module, 'port'):
                module.port = 6667

            if not hasattr(module, 'password'):
                module.password = None

            if not hasattr(module, 'ssl'):
                module.ssl = False

            if hasattr(module, 'host') and module.host == 'irc.example.net':
                error = "\n".join([
                    'Error: you must edit the config file first!',
                    "You're currently using {0}".format(module.filename)
                ])
                print >> sys.stderr, error
                sys.exit(1)

            config_modules.append(module)


#!/usr/bin/env python
"""
reload.py - jenni Module Reloader Module
Copyright 2009-2013, Michael Yanovich (yanovich.net)
Copyright 2008-2013, Sean B. Palmer (inamidst.com)
Licensed under the Eiffel Forum License 2.

More info:
 * jenni: https://github.com/myano/jenni/
 * Phenny: http://inamidst.com/phenny/
"""

import sys, os.path, time, imp
import irc

def f_reload(jenni, input):
    """Reloads a module, for use by admins only."""
    if not input.admin: return

    name = input.group(2)
    if name == jenni.config.owner:
        return jenni.reply('What?')

    if (not name) or (name == '*'):
        jenni.variables = None
        jenni.commands = None
        jenni.setup()
        return jenni.reply('done')

    if not sys.modules.has_key(name):
        return jenni.reply('%s: no such module!' % name)

    # Thanks to moot for prodding me on this
    path = sys.modules[name].__file__
    if path.endswith('.pyc') or path.endswith('.pyo'):
        path = path[:-1]
    if not os.path.isfile(path):
        return jenni.reply('Found %s, but not the source file' % name)

    module = imp.load_source(name, path)
    sys.modules[name] = module
    if hasattr(module, 'setup'):
        module.setup(jenni)

    mtime = os.path.getmtime(module.__file__)
    modified = time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime(mtime))

    jenni.register(vars(module))
    jenni.bind_commands()

    jenni.reply('%r (version: %s)' % (module, modified))
    if hasattr(jenni.config, 'logchan_pm'):
        if not input.owner:
            jenni.msg(jenni.config.logchan_pm, 'RELOADED: %r -- (%s, %s) - %s' % (module, input.sender, input.nick, modified))
f_reload.name = 'reload'
f_reload.rule = ('$nick', ['reload'], r'(\S+)?')
f_reload.priority = 'low'
f_reload.thread = False

if __name__ == '__main__':
    print __doc__.strip()

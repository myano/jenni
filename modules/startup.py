#!/usr/bin/env python
"""
startup.py - jenni Startup Module
Copyright 2009-2013, Michael Yanovich (yanovich.net)
Copyright 2008-2013, Sean B. Palmer (inamidst.com)
Licensed under the Eiffel Forum License 2.

More info:
 * jenni: https://github.com/myano/jenni/
 * Phenny: http://inamidst.com/phenny/
"""

import threading, time

def setup(jenni):
    # by clsn
    jenni.data = {}
    refresh_delay = 300.0

    if hasattr(jenni.config, 'refresh_delay'):
        try: refresh_delay = float(jenni.config.refresh_delay)
        except: pass

        def close():
            print "Nobody PONGed our PING, restarting"
            jenni.handle_close()

        def pingloop():
            timer = threading.Timer(refresh_delay, close, ())
            jenni.data['startup.setup.timer'] = timer
            jenni.data['startup.setup.timer'].start()
            # print "PING!"
            jenni.write(('PING', jenni.config.host))
        jenni.data['startup.setup.pingloop'] = pingloop

        def pong(jenni, input):
            try:
                # print "PONG!"
                jenni.data['startup.setup.timer'].cancel()
                time.sleep(refresh_delay + 60.0)
                pingloop()
            except: pass
        pong.event = 'PONG'
        pong.thread = True
        pong.rule = r'.*'
        jenni.variables['pong'] = pong

        # Need to wrap handle_connect to start the loop.
        inner_handle_connect = jenni.handle_connect

        def outer_handle_connect():
            inner_handle_connect()
            if jenni.data.get('startup.setup.pingloop'):
                jenni.data['startup.setup.pingloop']()

        jenni.handle_connect = outer_handle_connect

def startup(jenni, input):
    import time

    if hasattr(jenni.config, 'serverpass') and not jenni.auth_attempted:
        jenni.write(('PASS', jenni.config.serverpass))

    if not jenni.is_authenticated and hasattr(jenni.config, 'password'):
        if hasattr(jenni.config, 'user') and jenni.config.user is not None:
            user = jenni.config.user
        else:
            user = jenni.config.nick

        jenni.msg('NickServ', 'IDENTIFY %s %s' % (user, jenni.config.password))
        time.sleep(10)

    # Cf. http://swhack.com/logs/2005-12-05#T19-32-36
    for channel in jenni.channels:
        jenni.write(('JOIN', channel))
        time.sleep(0.5)
startup.rule = r'(.*)'
startup.event = '251'
startup.priority = 'low'

# Method for populating op/hop/voice information in channels on join
def privs_on_join(jenni, input):
    if not input.mode_target or not input.mode_target.startswith('#'):
        return

    channel = input.mode_target
    if input.names and len(input.names) > 0:
        split_names = input.names.split()
        for name in split_names:
            nick_mode, nick = name[0], name[1:]
            if nick_mode == '@':
                jenni.add_op(channel, nick)
            elif nick_mode == '%':
                jenni.add_halfop(channel, nick)
            elif nick_mode == '+':
                jenni.add_voice(channel, nick)
privs_on_join.rule = r'(.*)'
privs_on_join.event = '353'
privs_on_join.priority = 'high'

# Method for tracking changes to ops/hops/voices in channels
def track_priv_change(jenni, input):
    if not input.sender or not input.sender.startswith('#'):
        return

    channel = input.sender

    if input.mode:
        add_mode = input.mode.startswith('+')
        del_mode = input.mode.startswith('-')

        # Check that this is a mode change and that it is a mode change on a user
        if (add_mode or del_mode) and input.mode_target and len(input.mode_target) > 0:
            mode_change = input.mode[1:]
            mode_target = input.mode_target

            if add_mode:
                if mode_change == 'o':
                    jenni.add_op(channel, mode_target)
                elif mode_change == 'h':
                    jenni.add_halfop(channel, mode_target)
                elif mode_change == 'v':
                    jenni.add_voice(channel, mode_target)
            else:
                if mode_change == 'o':
                    jenni.del_op(channel, mode_target)
                elif mode_change == 'h':
                    jenni.del_halfop(channel, mode_target)
                elif mode_change == 'v':
                    jenni.del_voice(channel, mode_target)
track_priv_change.rule = r'(.*)'
track_priv_change.event = 'MODE'
track_priv_change.priority = 'high'

if __name__ == '__main__':
    print __doc__.strip()

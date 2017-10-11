#!/usr/bin/env python
"""
sasl.py - jenni SASL Authentication module
"""
import base64

def irc_cap (jenni, input):
    cap, value = input.args[1], input.args[2]
    rq = ''

    if jenni.is_connected:
        return

    if cap == 'LS':
        if 'multi-prefix' in value:
            rq += ' multi-prefix'
        if 'sasl' in value:
            rq += ' sasl'

        if not rq:
            irc_cap_end(jenni, input)
        else:
            if rq[0] == ' ':
                rq = rq[1:]

            jenni.write(('CAP', 'REQ', ':' + rq))

    elif cap == 'ACK':
        if 'sasl' in value:
            jenni.write(('AUTHENTICATE', 'PLAIN'))
        else:
            irc_cap_end(jenni, input)

    elif cap == 'NAK':
        irc_cap_end(jenni, input)

    else:
        irc_cap_end(jenni, input)

    return
irc_cap.rule = r'(.*)'
irc_cap.event = 'CAP'
irc_cap.priority = 'high'


def irc_authenticated (jenni, input):
    auth = False
    if hasattr(jenni.config, 'nick') and jenni.config.nick is not None and hasattr(jenni.config, 'password') and jenni.config.password is not None:
        nick = jenni.config.nick
        password = jenni.config.password

        # If provided, use the specified user for authentication, otherwise just use the nick
        if hasattr(jenni.config, 'user') and jenni.config.user is not None:
            user = jenni.config.user
        else:
            user = nick

        auth = "\0".join((nick, user, password))
        auth = base64.b64encode(auth)

    if not auth:
        jenni.write(('AUTHENTICATE', '+'))
    else:
        while len(auth) >= 400:
            out = auth[0:400]
            auth = auth[401:]
            jenni.write(('AUTHENTICATE', out))

        if auth:
            jenni.write(('AUTHENTICATE', auth))
        else:
            jenni.write(('AUTHENTICATE', '+'))

    return
irc_authenticated.rule = r'(.*)'
irc_authenticated.event = 'AUTHENTICATE'
irc_authenticated.priority = 'high'


def irc_903 (jenni, input):
    jenni.is_authenticated = True
    irc_cap_end(jenni, input)
    return
irc_903.rule = r'(.*)'
irc_903.event = '903'
irc_903.priority = 'high'


def irc_904 (jenni, input):
    irc_cap_end(jenni, input)
    return
irc_904.rule = r'(.*)'
irc_904.event = '904'
irc_904.priority = 'high'


def irc_905 (jenni, input):
    irc_cap_end(jenni, input)
    return
irc_905.rule = r'(.*)'
irc_905.event = '905'
irc_905.priority = 'high'


def irc_906 (jenni, input):
    irc_cap_end(jenni, input)
    return
irc_906.rule = r'(.*)'
irc_906.event = '906'
irc_906.priority = 'high'


def irc_907 (jenni, input):
    irc_cap_end(jenni, input)
    return
irc_907.rule = r'(.*)'
irc_907.event = '907'
irc_907.priority = 'high'


def irc_001 (jenni, input):
    jenni.is_connected = True
    return
irc_001.rule = r'(.*)'
irc_001.event = '001'
irc_001.priority = 'high'


def irc_cap_end (jenni, input):
    jenni.write(('CAP', 'END'))
    return


if __name__ == '__main__':
    print __doc__.strip()

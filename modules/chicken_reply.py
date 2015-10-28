#!/usr/bin/env python

'''
chicken_reply.py - Chicken reply Module (Chicken butt, chicken thigh)
Copyright 2015, Kevin Holland (kevinholland94@gmail.com)
Licensed under the Eiffel Forum License 2.

NOTE: This module should be disabled by default, as it is sort of stupid and could be annoying.
This module will reply "Chicken butt" or "Chicken thigh" respectively to "why" or "what" messages in the channel.

Example:
    person | what?
    bot | person: chicken butt

More info:
 * jenni: https://github.com/myano/jenni/
 * Phenny: http://inamidst.com/phenny/
'''

import re

responses = {'what' : 'chicken butt',
             'why'  : 'chicken thigh',
             'wat'  : 'chicken bat',
             'where': 'chicken hair',
             'when' : 'chicken pen',
             'who'  : 'chicken poo',
             'how'  : 'chicken plow'}

def chicken_reply(jenni, input):
    question = re.sub('[?!]', '', input.groups()[0])
    message = responses[question.lower()]
    message = message.upper() if question.isupper() else message
    jenni.reply(message)

chicken_reply.rule = r'(?i)(^({qs})[\?\!]*$)'.format(qs="|".join(responses.keys()))
chicken_reply.priority = 'low'
chicken_reply.example = 'why?'
chicken_reply.thread = False

if __name__ == '__main__':
    print __doc__.strip()

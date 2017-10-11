#!/usr/bin/env python
'''
magic8ball.py - jenni's Magic 8 Ball Module
Copyright 2015, Kevin Holland (kevinholland94@gmail.com)
Licensed under the Eiffel Forum License 2.

This module is a Magic 8 Ball implementation that will give one answer for a question on a given day
This works by hashing the user's input and seeding it with the current date (as a string). This way,
the same question will always have the same answer on a given day.

More info:
 * jenni: https://github.com/myano/jenni/
 * Phenny: http://inamidst.com/phenny/
'''

import random
import hashlib
from time import time

random.seed()

def magic8Ball(jenni, input):
    #real yes or no answers
    answers = [ 'It is certain',
                'It is decidedly so',
                'Without a doubt',
                'Yes definitely',
                'You may rely on it',
                'As I see it, yes',
                'Most likely',
                'Outlook good',
                'Yes',
                'Signs point to yes',
                'Don\'t count on it',
                'My reply is no',
                'My sources say no',
                'Outlook not so good',
                'Very doubtful'
              ]

    #try again answer
    askAgainAnswers = [ 'Reply hazy try again',
                        'Ask again later',
                        'Better not tell you now',
                        'Cannot predict now',
                        'Concentrate and ask again'
                      ]

    #1 in 5 chance of getting an ask again answer (randint() is inclusive)
    if (random.randint(1,5) == 1):
        jenni.reply(random.choice(askAgainAnswers))
    else:  #else produce a real answer
        hash = hashlib.sha224(input)
        hash.update(str(time()))
        jenni.reply(answers[int(hash.hexdigest(), 16) % len(answers)])


magic8Ball.commands = ['magic8Ball', 'm8b']
magic8Ball.priority = 'low'
magic8Ball.example = '.m8b will it rain tomorrow?'

if __name__ == '__main__':
    print __doc__.strip()

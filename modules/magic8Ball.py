#!/usr/bin/env python
'''
magic8ball.py - jenni's Magic 8 Ball Module
Copyright 2015, Kevin Holland (kevinholland94@gmail.com)
Licensed under the Eiffel Forum License 2.

More info:
 * jenni: https://github.com/myano/jenni/
 * Phenny: http://inamidst.com/phenny/
'''

import random

random.seed()

def magic8Ball(jenni, input):
	answers = [	'It is certain',
				'It is decidedly so',
				'Without a doubt',
				'Yes definitely',
				'You may rely on it',
				'As I see it, yes',
				'Most likely',
				'Outlook good',
				'Yes',
				'Signs point to yes',
				'Reply hazy try again',
				'Ask again later',
				'Better not tell you now',
				'Cannot predict now',
				'Concentrate and ask again',
				'Don\'t count on it',
				'My reply is no',
				'My sources say no',
				'Outlook not so good',
				'Very doubtful']
	jenni.reply(random.choice(answers))

magic8Ball.commands = ['magic8Ball', 'm8b']
magic8Ball.priority = 'low'
magic8Ball.example = '.m8b will it rain tomorrow?'

if __name__ == '__main__':
    print __doc__.strip()

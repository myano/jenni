#!/usr/bin/env python
"""
insult.py - Jenni Insult Module
by alekhin0w

More info:
 * Jenni: https://github.com/myano/jenni/
 * Phenny: http://inamidst.com/phenny/
"""

def insult(jenni, input):
    """ insults <target> with random spanish insult """
    from random import choice
    target = input.group(2)
    if not target:
        return jenni.reply('.i <target>!')
    target.encode('utf-8')
    jenni.say(target + ': ' + choice(insult.insultList))

insult.commands = ['i']
insult.priority = 'medium'
insult.example = '.i <target>'
insult.insultList = ['puto', 'trolo', 'forro', 'insurrecto', 'trolita', 'kirchnerista', 'beligerantemente peronista', 'aguafiestas', 'actualizame esta gil', 'apestoso usuario de windows']

if __name__ == '__main__':
    print __doc__.strip()

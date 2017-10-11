#!/usr/bin/env python
"""
insult.py - Jenni Insult Module
by alekhin0w

More info:
 * Jenni: https://github.com/myano/jenni/
 * Phenny: http://inamidst.com/phenny/
"""
import os, random
from modules import unicode as uc

def insult(jenni, input):
    """ insults <target> with configured language insult """
    try:
        insultFilename = os.path.expanduser('~/.jenni/insult.'+ jenni.config.insult_lang +'.txt')
    except:
        jenni.say("You need to configure the default language!")
        return

    target = input.group(2)
    if not target:
        return jenni.reply('.i <target>!')
    target.encode('utf-8')
    target = (target).strip()
    try:
        fn = open(insultFilename, "r")
    except IOError as e:
        generateDatabase(jenni, insultFilename)
        fn = open(insultFilename, "r")
    lines = fn.readlines()
    fn.close()
    random.seed()
    jenni.say(target + ': ' + uc.decode(random.choice(lines)))

insult.commands = ['i']
insult.priority = 'medium'
insult.example = '.i <target>'

def addinsult(jenni, input):
    """.iadd <insult> -- adds a harsh adjetive to the insult database"""
    try:
        insultFilename = os.path.expanduser('~/.jenni/insult.'+ jenni.config.insult_lang +'.txt')
    except:
        jenni.say("You need to configure the default language!")
        return

    text = input.group(2)
    text = uc.encode(text)
    fn = open(insultFilename, "a")
    fn.write(text)
    fn.write("\n")
    fn.close()
    jenni.reply("Insult added.")
addinsult.commands = ['iadd']
addinsult.priority = 'medium'
addinsult.example = '.iadd Bad Person'
addinsult.rate = 30

def generateDatabase(jenni, insultFilename):
    if jenni.config.insult_lang == "english":
        insultList = ['fuck you', 'stupid', 'asshole', 'you suck']
    elif jenni.config.insult_lang == "spanish":
        insultList = ['puto', 'trolo', 'forro', 'insurrecto', 'trolita', 'aguafiestas', 'actualizame esta gil', 'apestoso usuario de windows']
    else:
        return # silent fail due lack of configuration
    fn = open(insultFilename, "a")

    for insult in insultList:
        fn.write(insult)
        fn.write("\n")
    fn.close()

    jenni.say(jenni.config.insult_lang + " insult database created.")

if __name__ == '__main__':
    print __doc__.strip()

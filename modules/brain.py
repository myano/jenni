#!/usr/bin/env python
"""
brain.py - Store data on disk
Copyright 2015, Britt Gresham (www.brittg.com)
Licensed under the Eiffel Forum License 2.

More info:
 * jenni: https://github.com/myano/jenni/
 * Phenny: http://inamidst.com/phenny/

This module allows other modules to store information in memory for other
modules to read from or write to. This module intentionally does not have any
user facing commands.

To save to a json file jenni's configuration needs to have a path specified in
jenni.config.brain['path'] otherwise data will only be stored in memory instead.

How to integrate brain.py into your module:

import random

def excuses(jenni, msg):
    if 'excuses' not in jenni.brain:
        jenni.brain['excuses'] = []
    excuse = msg.group(1)
    jenni.brain['excuses'].append(excuse)
    jenni.save()
excuses.commands = ['excuses']

def print_excuse(jenni, msg):
    excuses = jenni.brain.get('excuses')
    if excuses:
        jenni.reply(random.choice(excuses))
    else:
        jenni.reply('Add an excuse first')
print_excuse.commands = ['print_excuse']
"""

import os
import json


class Brain(dict):

    def __init__(self, jenni, brain_path=None):
        self.jenni = jenni
        self.brain_path = brain_path
        initial_data = {}
        if self.brain_path:
            self.brain_path = os.path.expanduser(self.brain_path)
            if os.path.isfile(self.brain_path):
                f = open(self.brain_path, 'r')
                payload = f.read()
                f.close()
                if payload:
                    initial_data = json.loads(payload)
        dict.__init__(self, initial_data)

    def save(self):
        if not self.brain_path:
            return
        with open(self.brain_path, 'w') as f:
            f.write(json.dumps(self))


def setup(jenni):
    brain_path = None
    if hasattr(jenni.config, 'brain'):
        brain_path = jenni.config.brain.get('path')

    jenni.brain = Brain(jenni, brain_path=brain_path)

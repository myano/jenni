#!/usr/bin/env python
"""
wikiquote.py - jenni Random Quote Module
Copyright 2009-2013, Michael Yanovich (yanovich.net)
Copyright 2008-2013, Sean B. Palmer (inamidst.com)
Licensed under the Eiffel Forum License 2.

Developed by kaneda (https://jbegleiter.com / https://github.com/kaneda)

More info:
 * jenni: https://github.com/myano/jenni/
 * Phenny: http://inamidst.com/phenny/
"""

import json
from random import randrange
import urllib

try:
    from BeautifulSoup import BeautifulSoup as Soup
except ImportError:
    raise ImportError("Could not find BeautifulSoup library,"
                      "please install to use the wikiquote module")

USER_AGENT = "JenniBot/1.0 (https://github.com/myano/jenni) JenniBot/1.0"

class JenniURLopener(urllib.FancyURLopener):
    version = USER_AGENT

urllib._urlopener = JenniURLopener()

BASE_URL = "https://en.wikiquote.org/w/api.php?format=json&"

LIMIT = "5000"
MAX_TRIES = 10

CATS = [
  "Category:Television_shows",
  "Category:Proverbs",
  "Category:Literary_works",
  "Category:Films",
  "Category:Philosophers"
]

CAT_PREFIX = "Category:"
IGNORE_PREFIX = "Wikiquote:"

SUBCATS = "action=query&list=categorymembers&cmtype=subcat|page&cmprop=ids|title|type&cmlimit=" + LIMIT + "&cmtitle=%s"
SECTIONS = "action=parse&prop=sections&pageid=%s"
SECTION = "action=parse&pageid=%i&section=%s"

def choose_random_member(members):
    num_members = len(members)
    if num_members == 0: return None

    num_tries = 0
    random_member = None

    # Try 10 times
    while random_member == None and num_tries < MAX_TRIES:
        random_member = members[randrange(num_members)]

        # We only want a page or a subcategory
        if random_member["title"].startswith(IGNORE_PREFIX):
            random_member = None

        num_tries += 1

    return random_member

def choose_random_section(sections):
    num_sections = len(sections)
    if num_sections == 0: return None

    num_tries = 0
    random_section = None

    # Try 10 times
    while random_section == None and num_tries < MAX_TRIES:
        random_section = sections[randrange(num_sections)]
        num_tries += 1

    return random_section

def random_quote(jenni, cat):
    if cat is not None:
        if cat not in CATS:
            jenni.say("I don't know that category, please select from one of: {0}".format(', '.join(CATS)))
            return
    else:
        cat = CATS[randrange(len(CATS))]

    page_title = page_id = None

    # First drill down to the lowest category
    while(True):
        try:
            cat_url = BASE_URL + SUBCATS % cat
            content = json.loads(urllib.urlopen(cat_url).read())
            cat_members = content["query"]["categorymembers"]

            # Select at random
            random_member = choose_random_member(cat_members)
            if random_member is None:
                jenni.say("An error occurred fetching a subcategory")
                return
            
            if random_member["type"] == "subcat":
                cat = random_member["title"]
            else:
                page_title = random_member["title"]
                page_id = random_member["pageid"]
                break
        except Exception as e:
            jenni.say("An error occurred fetching a quote: {0}".format(e))
            return

    # Next select a random quote from the page
    try:
        page_url = BASE_URL + SECTIONS % page_id
        content = json.loads(urllib.urlopen(page_url).read())
        sections = content["parse"]["sections"]

        quote = None
        num_tries = 0
        while quote == None and num_tries < MAX_TRIES:
            section = choose_random_section(sections)
    
            if section is None:
                jenni.say("We accidentally chose a page with no quotes, sorry about that!")
                return
    
            section_index = randrange(len(sections)) + 1
    
            section_url = BASE_URL + SECTION % (page_id, section_index)
            content = json.loads(urllib.urlopen(section_url).read())
            section_title = content["parse"]["title"]
            html = Soup(content["parse"]["text"]["*"])
            all_quotes = []
            for ul in html.findAll('ul'):
                for li in ul.findAll('li'):
                    all_quotes.append(li.text)
    
            for dd in html.findAll('dd'):
                all_quotes.append(dd.text.replace("<b>","").replace("</b>",""))
    
            len_all_quotes = len(all_quotes)
            if len_all_quotes == 0:
                num_tries += 1
            else:
                quote = all_quotes[randrange(len_all_quotes)]
    
        if quote is None:
          jenni.say("We accidentally chose a section of a page with no quotes, sorry about that!")
          return

        jenni.say("{0}: {1}".format(section_title, quote.encode('utf-8')))
    except Exception as e:
        jenni.say("An error occurred fetching a quote: {0}".format(e))
        return

def wikiquote(jenni, input):
    origterm = input.groups()[1]
    if origterm:
        origterm = origterm.encode('utf-8')
        origterm = origterm.strip()

    error = None

    random_quote(jenni, origterm)
wikiquote.commands = ['wq', 'wikiquote']
wikiquote.priority = 'low'
wikiquote.rate = 10

def list_cats(jenni, input):
    jenni.say("WikiQuote categories I know: {0}".format(", ".join(CATS)))
list_cats.commands = ['list_quote_cats', 'list_wikiquote_cats', 'ls_wq_cats']
list_cats.priority = 'low'

if __name__ == '__main__':
    print __doc__.strip()

#!/usr/bin/env python
"""
github_stats.py - jenni Github Info Module
Copyright 2009-2013, Michael Yanovich (yanovich.net)
Copyright 2008-2013, Sean B. Palmer (inamidst.com)
Licensed under the Eiffel Forum License 2.

Developed by kaneda (http://jbegleiter.com / https://github.com/kaneda)

More info:
 * jenni: https://github.com/myano/jenni/
 * Phenny: http://inamidst.com/phenny/
"""

import json
import random
import re
import traceback
import urllib2
import urlparse

# For information about the Github API check out https://developer.github.com/v3/

BASE_URL = "https://api.github.com"
DEFAULT_HEADER = { "Accept": "application/vnd.github.v3+json" }

def fetch_github(url, term):
    t = urllib2.quote(term)
    if '%' in term:
        t = urllib.quote(term.replace('%', ''))

    request = urllib2.Request(url % t, headers=DEFAULT_HEADER)

    try:
        content = json.loads(urllib2.urlopen(request).read())
        return content
    except Exception as e:
        jenni.say("An error occurred fetching information from Github: {0}".format(e))
        return None

# Search for repos
def github_search(jenni, term):
    search_url = BASE_URL + "/search/repositories?q=%s"

    content = fetch_github(search_url, term)
    if content is None: return

    if "items" in content:
        # Take no more than 5 entries
        list_names = min(len(content["items"]), 5)
        full_names = ", ".join([ x["full_name"] for x in content["items"][:5] ])
        jenni.say("Top {0} results: {1}".format(list_names, full_names))
    else:
        jenni.say("Couldn't find any repos matching your search term")

# List open PRs
def github_prs(jenni, project):
    pr_url = BASE_URL + "/repos/%s/pulls"

    content = fetch_github(pr_url, project)
    if content is None: return

    num_pulls = len(content)

    jenni.say("{0} has {1} open PRs".format(project, num_pulls))
    if num_pulls > 0:
        list_pulls = min(num_pulls, 5)
        titles = ", ".join([ x["title"] for x in content[:5] ])
        jenni.say("Latest {0} PRs: {1}".format(list_pulls, titles))

def github_contribs(jenni, project):
    contrib_url = BASE_URL + "/repos/%s/contributors"

    content = fetch_github(contrib_url, project)
    if content is None: return

    num_contribs = len(content)

    jenni.say("This repo has {0} contributors".format(num_contribs))
    if num_contribs > 0:
        list_contribs = min(num_contribs, 5)
        contribs = ", ".join([ "{0} ({1} contributions)".format(x["login"], x["contributions"]) for x in content[:5] ])
        jenni.say("Top {0} contributors: {1}".format(list_contribs, contribs))

# Jenni commands start here
def gh_search(jenni, input):
    origterm = input.groups()[1]
    if not origterm:
        return jenni.say('Perhaps you meant ".github_search repo"?')
    origterm = origterm.encode('utf-8')
    origterm = origterm.strip()

    error = None

    try:
        result = github_search(jenni, origterm)
    except IOError:
        error = "An error occurred connecting to Github"
        traceback.print_exc()
    except Exception as e:
        error = "An unknown error occurred: " + str(e)
        traceback.print_exc()
gh_search.commands = ['gh_search', 'github_search']
gh_search.priority = 'low'
gh_search.rate = 10

def gh_prs(jenni, input):
    origterm = input.groups()[1]
    if not origterm:
        return jenni.say('Perhaps you meant ".github_stats user/repo"?')
    origterm = origterm.encode('utf-8')
    origterm = origterm.strip()

    error = None

    try:
        result = github_prs(jenni, origterm)
    except IOError:
        error = "An error occurred connecting to Github"
        traceback.print_exc()
    except Exception as e:
        error = "An unknown error occurred: " + str(e)
        traceback.print_exc()
gh_prs.commands = ['gh_prs', 'github_prs']
gh_prs.priority = 'low'
gh_prs.rate = 10

def gh_contribs(jenni, input):
    origterm = input.groups()[1]
    if not origterm:
        return jenni.say('Perhaps you meant ".github_contribs user/repo"?')
    origterm = origterm.encode('utf-8')
    origterm = origterm.strip()

    error = None

    try:
        result = github_contribs(jenni, origterm)
    except IOError:
        error = "An error occurred connecting to Github"
        traceback.print_exc()
    except Exception as e:
        error = "An unknown error occurred: " + str(e)
        traceback.print_exc()
gh_contribs.commands = ['gh_contribs', 'github_contribs']
gh_contribs.priority = 'low'
gh_contribs.rate = 10

if __name__ == '__main__':
    print __doc__.strip()

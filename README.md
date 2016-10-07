Philly
=====

Philly is a fork of jenni which is a fork of phenny. Since the development for both of them seemed stopped we decided to create a fork.

Todo:
- Clean up not working or unwanted modules
- Move codebase to Python 3

#Commands (Work in progress)
- .rand arg1 arg2 - Generates a random integer between arg1 and arg2
- .fd, .fucking_dinner - Gets a fucking recommedation what you could eat tonight
- .tell nick x - Tells nick x as soon as he is active again
- .isup website - Checks if its online
- .imdb movie - Gets information about movie from imdb
- .man item - Gets man page and sends info as link and in query
- ..

OLD WIKI FROM JENNI:
=====
Installation & Configuration
============================
jenni requires python 2.7, jenni will not work with python 3.x.

1. Run ./jenni - this creates a default config file
2. Edit ~/.jenni/default.py
3. Run ./jenni - this now runs jenni with your settings

Enjoy!

Optional Dependencies
=====================

From Pip:
- *feedparser* - allows the optional rss.py and nws.py modules to work.
- *BeautifulSoup* - allows better output from DuckDuckGo in search.py, image_me module and animate_me_module to work, and allow more in-depth results for .calc
- *yelpapi* - allows you to use the food module

Google Developer API Key
========================

The YouTube module requires that you have a Google Developer API key in order to function. This key can be obtained by:

1. Go to the Google Developer Console at: https://console.developers.google.com/
2. Create or select a project.
3. In the sidebar on the left, expand *APIs & auth*. Next, click *APIs*. In the list of APIs, find and ensure that the *YouTube Data API* is enabled.
4. In the sidebar on the left, select *Credentials*.
5. Create a new *Public API access* key and choose *Server Key*. Copy the created API Key into the *google_dev_apikey* option in your config.

Best Practices
==============

- Give jenni '@' (ops) at your risk. This software is provided without warranty, without exception.
- You can no longer run jenni as the root user (euid = 0).
  - This is a huge security risk, amplifying the impact of any potential vulnerability.

Additional Info
===============

See https://github.com/myano/jenni/wiki for information about jenni/Phenny modules

Credits
=======

For a list of contributions to the jenni fork see the file CREDITS.

Sean B. Palmer, http://inamidst.com/sbp/ forked by Michael Yanovich, https://yanovich.net/

Jenni
=====

jenni is a python IRC bot maintained and developed by Michael Yanovich. This project was originally created by Sean B. Palmer.

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
- *BeautifulSoup* - allows better output from DuckDuckGo in search.py and animate_me_module to work, and allow more in-depth results for .calc
- *yelpapi* - allows you to use the food module

Google Developer API Key
========================

The YouTube and image_me modules require that you have a Google Developer API key in order to function. This key can be obtained by:

1. Go to the Google Developer Console at: https://console.developers.google.com/
2. Create or select a project.
3. In the sidebar on the left, expand *APIs & auth*. Next, click *APIs*. In the list of APIs, find and ensure that the *YouTube Data API* is enabled.
4. In the sidebar on the left, select *Credentials*.
5. Create a new *Public API access* key and choose *Server Key*. Copy the created API Key into the *google_dev_apikey* option in your config.

For the image_me module you will need to enable the "Custom Search" API (as you did with YouTube), and in the project settings ensure that "Image search" is enabled.

For the image_me module you will also need a custom search engine (cx) key, which can be obtained by (thanks to http://stackoverflow.com/a/37084643 for the instructions):
1. From the Google Custom Search homepage ( http://www.google.com/cse/ ), click Create a Custom Search Engine.
2. Type a name and description for your search engine.
3. Under Define your search engine, in the Sites to Search box, enter at least one valid URL (For now, just put www.anyurl.com to get past this screen. More on this later ).
4. Select the CSE edition you want and accept the Terms of Service, then click Next. Select the layout option you want, and then click Next.
5. Click any of the links under the Next steps section to navigate to your Control panel.
6. In the left-hand menu, under Control Panel, click Basics.
7. In the Search Preferences section, select Search the entire web but emphasize included sites.
8. Click Save Changes.
9. In the left-hand menu, under Control Panel, click Sites.
10. Delete the site you entered during the initial setup process.

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

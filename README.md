Installation &c.

1. Run ./jenni - this creates a default config file
2. Edit ~/.jenni/default.py
3. Run ./jenni - this now runs jenni with your settings

Enjoy!

Optional:

4. Run **pip install feedparser** to allow the optional rss.py and nws.py modules to work.
5. Run **pip install BeautifulSoup** to allow better output from DuckDuckGo in search.py
   and allow more indepth results for .calc

For a list of contributions to the jenni fork see the file CREDITS.

It is **not** recommended to give jenni ops. If you do give jenni ops, you are doing so at ***your* own RISK**.

**I'm getting "Refusing to run as root". What do I do?**
Don't run jenni as root. It's a terrible idea, as it opens you up to a huge security risk. Should someone find a way to do something nasty with jenni, it may do much more damage if run as root. Please do yourself and everyone else a favor and run it under another user account.

--
Sean B. Palmer, http://inamidst.com/sbp/ forked by Michael Yanovich, https://yanovich.net/

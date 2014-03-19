import threading, json, dateutil.parser, time, datetime
import web

timerTask = None
bot = None
lastUpdate = None

def toggleUpdates(jenni, input):
	global timerTask
	global bot
	if input.owner:
		if timerTask is None:
			timerTask = threading.Timer(30.0, checkUpdates)
			timerTask.start()
			bot = jenni
			jenni.say("NSWiki Update Logging Enabled")
			checkUpdates()
		else:
			timerTask.cancel()
			timerTask = None
			jenni.say("NSWiki Update Logging Disabled")
	else:
		jenni.say("You lack permission.")

toggleUpdates.priority = 'high'
toggleUpdates.commands = ['toggle-updates']

def checkUpdates():
	global timerTask
	global bot
	global lastUpdate
	timerTask = threading.Timer(30.0, checkUpdates)
	timerTask.start()
	bytes = web.get("http://nswiki.org/api.php?action=query&list=recentchanges&rcshow=!bot&rcprop=title|user|comment|timestamp|loginfo&format=json")
	data = json.loads(bytes.decode("UTF-8"))
	for change in reversed(data["query"]["recentchanges"]):
		timestamp = dateutil.parser.parse(change["timestamp"])
		timestamp = timestamp.astimezone(dateutil.tz.tzutc())
		utime = unix_time(timestamp)
		if (lastUpdate is None) or utime > lastUpdate:
			lastUpdate = utime
			bot.say(formatWikiChange(timestamp, change))
			if len(change["comment"]) > 0:
				bot.say("   Comment: " + '\x03' + '04' + change["comment"]);

def formatWikiChange(time, change):
	str = time.strftime("%b %d, %Y at [%H:%M:%S] ")
	if change["type"] == "edit":
		str += change["user"] + " edited http://nswiki.org/" + change["title"].replace(" ", "_")
	elif change["type"] == "new":
		str += change["user"] + " created http://nswiki.org/" + change["title"].replace(" ", "_")
	elif change["type"] == "log":
		if change["logtype"] == "delete":
			str += change["user"] + " deleted http://nswiki.org/" + change["title"].replace(" ", "_")
		elif change["logtype"] == "newusers":
			str += change["title"].split(":")[1] + " user account created"
		elif change["logtype"] == "upload":
			str += change["user"] + " uploaded http://nswiki.org/" + change["title"].replace(" ", "_")
		else:
			str += change["user"] + " " + change["logtype"] + " "
	else:
		str += change["type"] + " "

	return str

def unix_time(dt):
    epoch = datetime.datetime.utcfromtimestamp(0)
    delta = dt.replace(tzinfo=None) - epoch.replace(tzinfo=None)
    return delta.total_seconds()

def unix_time_millis(dt):
    return unix_time(dt) * 1000.0
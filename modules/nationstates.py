
def nation(jenni, input):
	nation = input.group(2).lower().replace(" ", "_")
	jenni.say("https://www.nationstates.net/nation=" + nation)
nation.priority = 'high'
nation.commands = ['nation']

def region(jenni, input):
	region = input.group(2).lower().replace(" ", "_")
	jenni.say("https://www.nationstates.net/region=" +region)
region.priority = 'high'
region.commands = ['region']
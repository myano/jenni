#1/usr/bin/env/python
"""
food.py - Jenni Food Module
by afuhrtrumpet

More info:
 * jenni: https://github.com/myano/jenni/
 * Phenny: http://inamidst.com/phenny/
"""

from yelpapi import YelpAPI
import random


def food(jenni, input):
    if not hasattr(jenni.config, 'yelp_api_credentials'):
        return
    yelp_api = YelpAPI(jenni.config.yelp_api_credentials['consumer_key'], jenni.config.yelp_api_credentials['consumer_secret'], jenni.config.yelp_api_credentials['token'], jenni.config.yelp_api_credentials['token_secret'])

    location = input.group(2)

    if not location:
        jenni.say("Please enter a location.")
        return

    done = False
    max_offset = 5

    try:
        while not done:
            offset = random.randint(0, max_offset)
            response = yelp_api.search_query(category_filter="restaurants", location=location, limit=20, offset=offset)
            if len(response['businesses']) > 0:
                done = True
                jenni.say("How about, " + response['businesses'][random.randint(0, len(response['businesses']) - 1)]['name'] + "?")
            else:
                max_offset = offset - 1
    except YelpAPI.YelpAPIError:
        jenni.say("Invalid location!")

food.commands = ["food"]
food.priority = 'medium'
food.example = '.food <location>'

if __name__ == '__main__':
    print __doc__.strip()

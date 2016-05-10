#!/usr/bin/env python
"""
cleverbot.py - jenni's Cleverbot API module
Copyright 2013-2015 Michael Yanovich (yanovich.net)
Copyright 2013-2015 Rodney Folz, (github.com/folz)
Licensed under the Eiffel Forum License 2.

More info:
 * jenni: https://github.com/myano/jenni/
 * Phenny: http://inamidst.com/phenny/
 * https://github.com/folz/cleverbot.py

This library lets you open chat session with cleverbot (www.cleverbot.com)

Example of how to use the bindings:

>>> import cleverbot
>>> cb = cleverbot.Cleverbot()
>>> print cb.ask('Hello there')
'Hello.'

"""

#import cookielib
import collections
import hashlib
import requests
from requests.compat import urlencode
from future.backports.html import parser

# Only use the instance method `unescape` of entity_parser. (I wish it was a
# static method or public function; it never uses `self` anyway)
entity_parser = parser.HTMLParser()


class Cleverbot:
    """
    Wrapper over the Cleverbot API.

    """
    HOST = "www.cleverbot.com"
    PROTOCOL = "http://"
    RESOURCE = "/webservicemin"
    API_URL = PROTOCOL + HOST + RESOURCE

    headers = {
        'User-Agent': 'Mozilla/4.0 (compatible; MSIE 8.0; Windows NT 6.0)',
        'Accept': 'text/html,application/xhtml+xml,'
                  'application/xml;q=0.9,*/*;q=0.8',
        'Accept-Charset': 'ISO-8859-1,utf-8;q=0.7,*;q=0.7',
        'Accept-Language': 'en-us,en;q=0.8,en-us;q=0.5,en;q=0.3',
        'Cache-Control': 'no-cache',
        'Host': HOST,
        'Referer': PROTOCOL + HOST + '/',
        'Pragma': 'no-cache'
    }

    def __init__(self):
        """ The data that will get passed to Cleverbot's web API """
        self.data = collections.OrderedDict(
            (
                # must be the first pairs
                ('stimulus', ''),
                ('cb_settings_language', ''),
                ('cb_settings_scripting', 'no'),
                ('islearning', 1),  # Never modified
                ('icognoid', 'wsf'),  # Never modified
                ('icognocheck', ''),

                ('start', 'y'),  # Never modified
                ('sessionid', ''),
                ('vText8', ''),
                ('vText7', ''),
                ('vText6', ''),
                ('vText5', ''),
                ('vText4', ''),
                ('vText3', ''),
                ('vText2', ''),
                ('fno', 0),  # Never modified
                ('prevref', ''),
                ('emotionaloutput', ''),  # Never modified
                ('emotionalhistory', ''),  # Never modified
                ('asbotname', ''),  # Never modified
                ('ttsvoice', ''),  # Never modified
                ('typing', ''),  # Never modified
                ('lineref', ''),
                ('sub', 'Say'),  # Never modified
                ('cleanslate', False),  # Never modified
            )
        )

        """
            ('stimulus': ''),
            ('start': 'y'),
            ('sessionid': ''),
            ('vText8': ''),
            ('vText7': ''),
            'vText6': '',
            'vText5': '',
            'vText4': '',
            'vText3': '',
            'vText2': '',
            'icognoid': 'wsf',  # Never modified
            'icognocheck': '',
            'fno': 0,  # Never modified
            'prevref': '',
            'emotionaloutput': '',  # Never modified
            'emotionalhistory': '',  # Never modified
            'asbotname': '',  # Never modified
            'ttsvoice': '',  # Never modified
            'typing': '',  # Never modified
            'lineref': '',
            'sub': 'Say',  # Never modified
            'islearning': 1,  # Never modified
            'cleanslate': False,  # Never modified
        }

        """

        # the log of our conversation with Cleverbot
        self.conversation = []

        # get the main page to get a cookie (see bug  #13)
        self.session = requests.Session()
        self.session.get(Cleverbot.PROTOCOL + Cleverbot.HOST)


    def ask(self, question):
        """Asks Cleverbot a question.

        Maintains message history.

        :param question: The question to ask
        :return Cleverbot's answer
        """

        # Set the current question
        self.data['stimulus'] = question

        # Connect to Cleverbot's API and remember the response
        resp = self._send()

        # Add the current question to the conversation log
        self.conversation.append(question)

        parsed = self._parse(resp.text)

        # Set data as appropriate
        if self.data['sessionid'] != '':
            self.data['sessionid'] = parsed['conversation_id']

        # Add Cleverbot's reply to the conversation log
        self.conversation.append(parsed['answer'])

        return parsed['answer']

    def _send(self):
        """POST the user's question and all required information to the
        Cleverbot API

        Cleverbot tries to prevent unauthorized access to its API by
        obfuscating how it generates the 'icognocheck' token. The token is
        currently the md5 checksum of the 10th through 36th characters of the
        encoded data. This may change in the future.

        TODO: Order is not guaranteed when urlencoding dicts. This hasn't been
        a problem yet, but let's look into ordered dicts or tuples instead.
        """
        # Set data as appropriate
        if self.conversation:
            linecount = 1
            for line in reversed(self.conversation):
                linecount += 1
                self.data['vText' + str(linecount)] = line
                if linecount == 8:
                    break

        # Generate the token
        enc_data = urlencode(self.data)
        digest_txt = enc_data[9:35]
        token = hashlib.md5(digest_txt.encode('utf-8')).hexdigest()
        self.data['icognocheck'] = token

        # POST the data to Cleverbot's API and return
        return self.session.post(Cleverbot.API_URL,
                                 data=self.data,
                                 headers=Cleverbot.headers)

    @staticmethod
    def _parse(resp_text):
        """Parses Cleverbot's response"""
        resp_text = entity_parser.unescape(resp_text)
        parsed = [
            item.split('\r') for item in resp_text.split('\r\r\r\r\r\r')[:-1]
        ]

        if parsed[0][1] == 'DENIED':
            raise CleverbotAPIError()

        parsed_dict = {
            'answer': parsed[0][0],
            'conversation_id': parsed[0][1],
        }
        try:
            parsed_dict['unknown'] = parsed[1][-1]
        except IndexError:
            parsed_dict['unknown'] = None
        return parsed_dict


if __name__ == '__main__':
    print __doc__.strip()
    main()

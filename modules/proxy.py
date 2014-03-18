#!/usr/bin/env python
"""
proxy.py - Web Facilities

More info:
 * Willie: https://willie.dftba.net
 * jenni: https://github.com/myano/jenni/
 * Phenny: http://inamidst.com/phenny/
"""

import json
import re
import urllib


class Grab(urllib.URLopener):
    def __init__(self, *args):
        self.version = 'Mozilla/5.0 (Windows NT 6.1; rv:24.0) Gecko/20100101 Firefox/24.0'
        urllib.URLopener.__init__(self, *args)

    def http_error_default(self, url, fp, errcode, errmsg, headers):
        return urllib.addinfourl(fp, [headers, errcode], "http:" + url)
urllib._urlopener = Grab()


def remote_call(uri):
    import json
    pyurl = u'https://tumbolia.appspot.com/py/'
    code = 'import simplejson;'
    code += "req=urllib2.Request(%s, headers={'Accept':'*/*'});"
    code += "req.add_header('User-Agent', 'Mozilla/5.0');"
    code += "u=urllib2.urlopen(req);"
    code += "rtn=dict();"
    code += "rtn['headers'] = u.headers.dict;"
    code += "contents = u.read();"
    code += "con = str();"
    code += r'''exec "try: con=(contents).decode('utf-8')\n'''
    code += '''except: con=(contents).decode('iso-8859-1')";'''
    code += "rtn['read'] = con;"
    code += "rtn['url'] = u.url;"
    code += "rtn['geturl'] = u.geturl();"
    code += "print simplejson.dumps(rtn)"
    query = code % repr(uri)
    temp = urllib.quote(query)
    u = urllib.urlopen(pyurl + temp)
    results = u.read()
    u.close()

    try:
        useful = json.loads(results)
        return True, useful
    except Exception, error:
        return False, str(results)


def get(uri):
    if not uri.startswith('http'):
        return
    status, u = remote_call(uri)
    if status:
        page = u['read']
    else:
        page = str()
    return page


if __name__ == "__main__":
    print __doctype__.strip()

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
import time

user_agent = 'Mozilla/5.0 (Windows NT 6.1; rv:38.0) Gecko/20100101 Firefox/38.0'


class Grab(urllib.URLopener):
    def __init__(self, *args):
        self.version = user_agent
        urllib.URLopener.__init__(self, *args)

    def http_error_default(self, url, fp, errcode, errmsg, headers):
        return urllib.addinfourl(fp, [headers, errcode], "http:" + url)
urllib._urlopener = Grab()


def remote_call(uri, info=False):
    pyurl = u'https://tumbolia-two.appspot.com/py/'
    code = 'import json;'
    #code += "req=urllib2.Request(%s,headers={'Accept':'*/*'});"
    #code += "req.add_header('User-Agent','%s');" % (user_agent)
    #code += "u=urllib2.urlopen(req);"

    code += 'opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(),'
    code += 'urllib2.BaseHandler(), urllib2.HTTPHandler(),'
    code += 'urllib2.HTTPRedirectHandler(), urllib2.HTTPErrorProcessor(),'
    code += 'urllib2.UnknownHandler());'
    code += 'urllib2.install_opener(opener);'
    code += "req=urllib2.Request(%s, headers={'Accept':'*/*'});"
    code += "req.add_header('User-Agent', '%s');" % (user_agent)
    code += "u=urllib2.urlopen(req);"

    code += "rtn=dict();"
    if info:
        code += "rtn['info']=u.info();"
    else:
        code += "rtn['headers']=u.headers.dict;"
        code += "contents=u.read(2048);"
        code += "con=str();"
        code += r'''exec "try: con=(contents).decode('utf-8')\n'''
        code += '''except: con=(contents).decode('iso-8859-1')";'''
        code += "rtn['read']=con;"
        code += "rtn['url']=u.url;"
        code += "rtn['geturl']=u.geturl();"
        code += "rtn['code']=u.code;"
    code += "print json.dumps(rtn)"
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


def get_more(uri):
    if not uri.startswith('http'):
        uri = 'http://' + uri
    status, response = remote_call(uri)
    return status, response


def head(uri):
    if not uri.startswith('http'):
        uri = 'http://' + uri
    status, response = remote_call(uri, True)
    if status:
        page = u['info']
    else:
        page = str()
    return page


if __name__ == "__main__":
    print __doctype__.strip()

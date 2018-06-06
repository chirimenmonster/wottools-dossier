# -*- coding: utf-8 -*-

from SimpleHTTPServer import SimpleHTTPRequestHandler
from SocketServer import TCPServer
from urlparse import urlparse, parse_qs
import json
from datetime import datetime
import locale

from calcwn8 import getWN8

PORT = 8080

class MyHandler(SimpleHTTPRequestHandler):

    def do_HEAD(self):
        self.__result = None
        _, _, path, _, query, _ = urlparse(self.path)
        queryDict = parse_qs(query)
        if path != '/playerstats.json':
           self.send_error(404)
           return        
        if 'nickname' not in queryDict or len(queryDict['nickname']) != 1:
           self.send_error(404, 'parameter "nickname" is not specified')
           return
        try:
            nickname = queryDict['nickname'][0]
            wn8data, lastmodified = getWN8(nickname)
        except:
           self.send_error(404, 'player\'s stats is not found')
           return
           
        self.__result = json.dumps(wn8data, sort_keys=True)

        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.send_header('Content-Length', len(self.__result))
        self.send_header('Content-Disposition', 'filename="playerstats.json"')
        self.send_header('Last-Modified', datetime.utcfromtimestamp(lastmodified).strftime('%a, %d %b %Y %X GMT'))
        self.end_headers()


    def do_GET(self):
        self.do_HEAD()
        if self.__result is not None:
            self.wfile.write(self.__result)


locale.setlocale(locale.LC_ALL, 'C')
TCPServer.allow_use_reuse_address = True
httpd = TCPServer(('', PORT), MyHandler)
httpd.serve_forever()

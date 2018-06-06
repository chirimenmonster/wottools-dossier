# -*- coding: utf-8 -*-

from SimpleHTTPServer import SimpleHTTPRequestHandler
from SocketServer import TCPServer
from urlparse import urlparse, parse_qs
import json

from calcwn8 import getWN8

PORT = 8080

class MyHandler(SimpleHTTPRequestHandler):

    def do_GET(self):
        query = parse_qs(urlparse(self.path).query)
        if 'nickname' not in query or len(query['nickname']) != 1:
           self.send_error(404)
           return
        try:
            nickname = query['nickname'][0]
            wn8data = getWN8(nickname)
        except:
           self.send_error(404)
           return
           
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        
        self.wfile.write(json.dumps(wn8data, sort_keys=True))

        
httpd = TCPServer(('', PORT), MyHandler)
httpd.serve_forever()

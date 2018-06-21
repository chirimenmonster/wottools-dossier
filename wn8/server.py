# -*- coding: utf-8 -*-

import os
from SimpleHTTPServer import SimpleHTTPRequestHandler
from SocketServer import TCPServer
from urlparse import urlparse, parse_qs
import json
from datetime import datetime
import locale
import traceback
from collections import OrderedDict

from calcwn8 import getWN8
from wgapi import VehicleDatabase, URLError, WGAPIError

PORT = 8080

class MyHandler(SimpleHTTPRequestHandler, object):

    def do_HEAD(self):
        if not self.__directive(False):
            super(MyHandler, self).do_HEAD()

    def do_GET(self):
        if not self.__directive(True):
            super(MyHandler, self).do_GET()
    
    def __directive(self, requireBody):
        self.__result = None
        _, _, path, _, query, _ = urlparse(self.path)
        if path == '/playerstats.json':
            try:
                result, lastmodified = self.__getPlayerstats(query)
            except Exception as e:
                self.__sendError(e)
                return True
            self.__sendJSON(result, 'playerstats.json', lastmodified, requireBody)
            return True
        elif path == '/vehicledb.json':
            try:
                result, lastmodified = self.__getVehicleDB(query)
            except Exception as e:
                self.__sendError(e)
                return True
            self.__sendJSON(result, 'vehicledb.json', lastmodified, requireBody)
            return True
        _, ext = os.path.splitext(path)
        if path != '/' and ext not in ( '.html', '.css', '.js', '.jpg', '.png', '.ico' ):
           self.send_error(404)
           return True
        return False

    def __sendJSON(self, data, filename, lastmodified, requireBody):
        result = json.dumps(OrderedDict((('status', 'success'), ('result', data))))
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.send_header('Content-Length', len(result))
        self.send_header('Content-Disposition', 'filename="{}"'.format(filename))
        self.send_header('Last-Modified', datetime.utcfromtimestamp(lastmodified).strftime('%a, %d %b %Y %X GMT'))
        self.end_headers()
        if requireBody:
            self.wfile.write(result)

    def __sendError(self, error):
        if isinstance(error, WGAPIError):
            code = 404
            message = '{}: {}'.format(error, error.description)
            result = json.dumps({
                'status': 'error',
                'error': {
                    'code': code,
                    'message': str(error),
                    'description': error.description,
                    'url': error.filename
                }
            })
        elif isinstance(error, URLError):
            code = 500
            result = json.dumps({
                'status': 'error',
                'error': {
                    'code': code,
                    'message': str(error.reason),
                    'url': error.filename
                }
            })
        else:
            code = 500
            message = 'unknown error'
            result = json.dumps({
                'status': 'error',
                'error': {
                    'code': code,
                    'message': message,
                    'error': str(error),
                    'traceback': traceback.format_exc()
                }
            })
        self.send_response(code)
        self.send_header('Content-type', 'application/json')
        self.send_header('Content-Length', len(result))
        self.end_headers()
        self.wfile.write(result)   
        
    def __getPlayerstats(self, query):
        queryDict = parse_qs(query)
        if 'nickname' not in queryDict or len(queryDict['nickname']) != 1:
           result = { 'code': 400, 'message': 'Bad Request', 'value': 'parameter "nickname" is not specified' }
           raise WGAPIError(result, '')
        nickname = queryDict['nickname'][0]
        wn8data, lastmodified = getWN8(nickname)
        return wn8data, lastmodified   

    def __getVehicleDB(self, query):
        vehicleDB = VehicleDatabase()
        data = vehicleDB.dumpAlt()
        lastmodified = vehicleDB.lastmodifiedAlt
        return data, lastmodified   
    

locale.setlocale(locale.LC_ALL, 'C')
TCPServer.allow_use_reuse_address = True
httpd = TCPServer(('', PORT), MyHandler)
httpd.serve_forever()

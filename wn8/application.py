from wsgiref.simple_server import make_server
import json
from collections import OrderedDict

from wgapi import VehicleDatabase

HOST = ''
PORT = 8080

class AppClass(object):
    def __init__(self, environ, start_response):
        self.environ = environ
        self.start_response = start_response
        print 'PATH_INFO = ', environ['PATH_INFO']
        print 'QUERY_STRING = ', environ['QUERY_STRING']
        
    def __iter__(self):
        try:
            data, lastmodified = self.__getVehicleDB(None)
            status = ('success', 200, 'OK')
            result = ('result', data)
            #raise
        except:
            status = ('error', 500, 'Internal Server Error')
            result = ('error', {
                'code': status[1],
                'message': status[2],
                'url': ''
            })
        result = json.dumps(OrderedDict((('status', status[0]), result)))
        response_headers = [
            ('Content-Type', 'application/json'),
            ('Content-Length', str(len(result)))           
        ]
        self.start_response('{} {}'.format(status[1], status[2]), response_headers)
        yield result

    def __getVehicleDB(self, query):
        vehicleDB = VehicleDatabase()
        data = vehicleDB.dumpAlt()
        lastmodified = vehicleDB.lastmodifiedAlt
        return data, lastmodified


if __name__ == '__main__':
    httpd = make_server(HOST, PORT, AppClass)
    httpd.serve_forever()

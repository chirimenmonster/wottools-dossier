
import os
import urllib
import json
from datetime import datetime
import time

CACHE_DIR = 'cache'
CACHE_WN8EXP = os.path.join(CACHE_DIR, 'wn8exp.json')
URL_WN8EXP = 'https://static.modxvm.com/wn8-data-exp/json/wn8exp.json'


class WN8Exp(object):

    def __init__(self):
        if not self.isExistsCache():
            result = self.fetch()
        self.read()

    def isExistsCache(self):
        if not os.path.exists(CACHE_WN8EXP):
            return False
        s = os.stat(CACHE_WN8EXP)
        if time.mktime(datetime.now().timetuple()) - s.st_mtime > 60 * 60 * 24:
            return False
        return True

    def fetch(self):
        if not os.path.exists(CACHE_DIR):
            os.mkdir(CACHE_DIR)
        result = urllib.urlretrieve(URL_WN8EXP, CACHE_WN8EXP)
        return result

    def read(self):
        with open(CACHE_WN8EXP, 'r') as fp:
            cache = json.load(fp)
        self.__data = {}
        for row in cache['data']:
            self.__data[str(row['IDNum'])] = row

    def getExpectedValue(self, tankId):
        return self.__data[str(tankId)]


if __name__ == '__main__':
    wn8 = WN8Exp()
    result = wn8.getExpectedValue(59681)
    print result

import os
import urllib
import json
from datetime import datetime
import time

URL_WGAPI = 'https://api.worldoftanks.asia'
APPLICATION_ID = 'demo'
accountId = '2003019760'

CACHE_DIR = 'cache'
CACHE_VEHICLE_DATABASE = os.path.join(CACHE_DIR, 'vehicledb.json')
CACHE_PLAYER_VEHICLES = os.path.join(CACHE_DIR, 'playervehicles.json')
CACHE_PLAYER_VEHICLE_STATS = os.path.join(CACHE_DIR, 'playervehiclestats.json')


class VehicleDatabase(object):

    def __init__(self):
        self.__cache = None
        if not self.isExistsCache():
            result = self.fetch()
        self.read()

    def isExistsCache(self):
        if not os.path.exists(CACHE_VEHICLE_DATABASE):
            return False
        s = os.stat(CACHE_VEHICLE_DATABASE)
        if time.mktime(datetime.now().timetuple()) - s.st_mtime > 60 * 60 * 24 * 7:
            return False
        return True

    def fetch(self):
        if not os.path.exists(CACHE_DIR):
            os.mkdir(CACHE_DIR)
        url = URL_WGAPI + '/wot/encyclopedia/vehicles/'
        param = {
            'application_id': APPLICATION_ID,
            'fields': 'tank_id,tag,name,nation,tier,type'
        }
        response = urllib.urlopen(url + '?' + urllib.urlencode(param)).read()
        self.__cache = json.loads(response)
        with open(CACHE_VEHICLE_DATABASE, 'w') as fp:
            json.dump(self.__cache, fp)

    def read(self):
        if self.__cache:
            return
        with open(CACHE_VEHICLE_DATABASE, 'r') as fp:
            self.__cache = json.load(fp)

    def get(self, tankId):
        return self.__cache['data'][str(tankId)]

        
class PlayerNames(object):

    def __init__(self, accountName):
        self.__cache = None
        self.__accountId = accountId
        self.__cacheDir = CACHE_DIR
        self.__cacheFile = os.path.join(self.__cacheDir, 'playernames.json')
        if not self.isExistsCache():
            result = self.fetch()
        self.read()

    def isExistsCache(self):
        if not os.path.exists(self.__cacheFile):
            return False
        s = os.stat(self.__cacheFile)
        if time.mktime(datetime.now().timetuple()) - s.st_mtime > 60 * 60 * 24 * 1:
            return False
        return True

    def fetch(self):
        url = URL_WGAPI + '/wot/account/list'
        param = {
            'application_id': APPLICATION_ID,
            'search': self.__accountName,
            'type': 'exact'
        }
        response = urllib.urlopen(url + '?' + urllib.urlencode(param)).read()
        result = json.loads(response)
        self.__cache[result['data']['nickname']] = result['data']['accontId']
        if not os.path.exists(self.__cacheDir):
            os.mkdir(self.__cacheDir)
        with open(self.__cacheFile, 'w') as fp:
            json.dump(self.__cache, fp)

    def read(self):
        if self.__cache:
            return
        with open(self.__cacheFile, 'r') as fp:
            self.__cache = json.load(fp)


class PlayerVehicles(object):

    def __init__(self, accountId):
        self.__cache = None
        self.__accountId = accountId
        self.__cacheDir = CACHE_DIR
        self.__cacheFile = os.path.join(self.__cacheDir, 'playervehicles_{}.json'.format(accountId))
        if not self.isExistsCache():
            result = self.fetch()
        self.read()

    def isExistsCache(self):
        if not os.path.exists(self.__cacheFile):
            return False
        s = os.stat(self.__cacheFile)
        if time.mktime(datetime.now().timetuple()) - s.st_mtime > 60 * 60 * 24 * 1:
            return False
        return True

    def fetch(self):
        if not os.path.exists(self.__cacheDir):
            os.mkdir(self.__cacheDir)
        url = URL_WGAPI + '/wot/account/tanks/'
        param = {
            'application_id': APPLICATION_ID,
            'account_id': self.__accountId,
            'fields': 'tank_id'
        }
        response = urllib.urlopen(url + '?' + urllib.urlencode(param)).read()
        self.__cache = json.loads(response)
        with open(self.__cacheFile, 'w') as fp:
            json.dump(self.__cache, fp)

    def read(self):
        if self.__cache:
            return
        with open(self.__cacheFile, 'r') as fp:
            self.__cache = json.load(fp)

    def dump(self):
        return self.__cache

    def list(self):
        return [ v['tank_id'] for v in self.__cache['data'][self.__accountId] ]


class PlayerVehicleStats(object):

    def __init__(self, accountId):
        self.__cache = None
        self.__accountId = accountId
        self.__cacheDir = CACHE_DIR
        self.__cacheFile = os.path.join(self.__cacheDir, 'playervehiclestats_{}.json'.format(accountId))
        if not self.isExistsCache():
            result = self.fetch()
        self.read()

    def isExistsCache(self):
        if not os.path.exists(self.__cacheFile):
            return False
        s = os.stat(self.__cacheFile)
        if time.mktime(datetime.now().timetuple()) - s.st_mtime > 60 * 60 * 24 * 1:
            return False
        return True

    def __fetch(self, tankList):
        url = URL_WGAPI + '/wot/tanks/stats/'
        param = {
            'application_id': APPLICATION_ID,
            'account_id': self.__accountId,
            'tank_id': ','.join(map(str, tankList)),
            'extra': 'random',
            'fields': 'tank_id,random.battles,random.wins,random.spotted,random.frags,random.damage_dealt,random.dropped_capture_points'
        }
        response = urllib.urlopen(url + '?' + urllib.urlencode(param)).read()
        return json.loads(response)

    def fetch(self):
        playerVehicles = PlayerVehicles(self.__accountId)
        list = playerVehicles.list()
        self.__cache = {}
        while len(list) > 0:
            if len(list) > 100:
                curr = list[:100]
                list = list[100:]
            else:
                curr = list
                list = []
            result = self.__fetch(curr)
            for stats in result['data'][self.__accountId]:
                self.__cache[str(stats['tank_id'])] = stats
        if not os.path.exists(self.__cacheDir):
            os.mkdir(self.__cacheDir)
        with open(self.__cacheFile, 'w') as fp:
            json.dump(self.__cache, fp)

    def read(self):
        if self.__cache:
            return
        with open(self.__cacheFile, 'r') as fp:
            self.__cache = json.load(fp)

    def dump(self):
        return self.__cache
    
    def get(self, tankId):
        return self.__cache[str(tankId)]



if __name__ == '__main__':
    vehicleDatabase = VehicleDatabase()
    result = vehicleDatabase.get(59681)
    print result
    
    playerVehicles = PlayerVehicles(accountId)
    result = playerVehicles.list()
    print result

    playerVehicleStats = PlayerVehicleStats(accountId)
    result = playerVehicleStats.dump()
    print result
    print len(result)
    result = playerVehicleStats.get(897)
    print result

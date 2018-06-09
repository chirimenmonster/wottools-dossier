import os
import urllib
import urllib2
import json
from time import time

URL_WGAPI = 'https://api.worldoftanks.asia'
APPLICATION_ID = 'demo'

CACHE_DIR = 'cache'

NATION_NAMES = ('ussr', 'germany', 'usa', 'china', 'france', 'uk', 'japan', 'czech', 'sweden', 'poland', 'italy')
VEHICLE_CLASSES = ('lightTank', 'mediumTank', 'heavyTank', 'SPG', 'AT-SPG')
VEHICLE_ORDER = ('lightTank', 'mediumTank', 'heavyTank', 'AT-SPG', 'SPG')
VEHICLE_TYPES = ('LT', 'MT', 'HT', 'SPG', 'TD')

class CachedDatabase(object):
    cache = None
    cacheLifetime = 0
    cacheDir = CACHE_DIR
    cacheFile = None
    sourceURL = None
    requestParam = None

    def __init__(self, config={}):
        self.config = config
        if config.get('force', False) or not self.isExistsCache():
            self.fetch()
        self.readCache()

    @property
    def cachePath(self):
        return os.path.join(self.cacheDir, self.cacheFile)

    def isExistsCache(self):
        if not os.path.exists(self.cachePath):
            return False
        stat = os.stat(self.cachePath)
        if time() - stat.st_mtime > self.cacheLifetime:
            return False
        return True

    def saveCache(self):
        if not os.path.exists(self.cacheDir):
            os.mkdir(self.cacheDir)
        with open(self.cachePath, 'w') as fp:
            json.dump(self.cache, fp)
        self.lastmodified = os.stat(self.cachePath).st_mtime

    def readCache(self):
        if self.cache:
            return
        if os.path.exists(self.cachePath):
            with open(self.cachePath, 'r') as fp:
                self.cache = json.load(fp)
            self.lastmodified = os.stat(self.cachePath).st_mtime

    def fetchJSON(self, url, param):
        if param:
            url += '?' + urllib.urlencode(param)
        response = urllib2.urlopen(url).read()
        return json.loads(response)

    def fetch(self):
        data = self.fetchJSON(self.sourceURL, self.requestParam)
        self.cache = data
        self.saveCache()
   
    def dump(self):
        return self.cache

    def keys(self):
        return self.cache.keys()

    def items(self):
        return self.cache.items()


class VehicleDatabase(CachedDatabase):
    cacheLifetime = 60 * 60 * 24 * 7
    cacheFile = 'vehicledb.json'
    cachePathAlt = '../vehiclelist.json'
    sourceURL = URL_WGAPI + '/wot/encyclopedia/vehicles/'
    requestParam = {
        'application_id': APPLICATION_ID,
        'fields': 'tank_id,tag,name,nation,tier,type'
    }
    def __init__(self, config={}):
        super(VehicleDatabase, self).__init__(config=config)
        self.index = {}
        self.index['nation'] = dict((n, i) for i, n in enumerate(NATION_NAMES))
        self.index['type'] = dict((n, i) for i, n in enumerate(VEHICLE_CLASSES))
        self.order = {}
        self.order['type'] = dict((n, i) for i, n in enumerate(VEHICLE_ORDER))

    def readCache(self):
        super(VehicleDatabase, self).readCache()
        if os.path.exists(self.cachePathAlt):
            with open(self.cachePathAlt, 'r') as fp:
                self.cacheAlt = json.load(fp)

    def get(self, tankId):
        result = self.cache['data'].get(str(tankId), None)
        if result is None:
            result = self.cacheAlt['data'].get(str(tankId), None)
        return result

    def getId(self, tankId, category):
        info = self.get(tankId)
        if info is None:
            return -1
        if category in self.index:
            return self.index[category][info[category]]
        return info[category]

    def getOrder(self, tankId, category):
        info = self.get(tankId)
        if info is None:
            return -1
        if category in self.order:
            return self.order[category][info[category]]
        return self.getId(tankId, category)

    def getType(self, tankId):
        vehicle = self.get(tankId)
        if vehicle is None:
            return ''
        return VEHICLE_TYPES[self.getId(tankId, 'type')]


class PlayerVehicles(CachedDatabase):
    cacheLifetime = 60 * 60 * 24 * 1
    sourceURL = URL_WGAPI + '/wot/account/tanks/'

    def __init__(self, accountId, config={}):
        self.__accountId = str(accountId)
        super(PlayerVehicles, self).__init__(config=config)

    @property
    def cacheFile(self):
        return 'playervehicles_{}.json'.format(self.__accountId)

    @property
    def requestParam(self):
        return {
            'application_id': APPLICATION_ID,
            'account_id': self.__accountId,
            'fields': 'tank_id'
        }

    def list(self):
        return [ v['tank_id'] for v in self.cache['data'][self.__accountId] ]


class PlayerVehicleStats(CachedDatabase):
    cacheLifetime = 60 * 60 * 24 * 1
    sourceURL = URL_WGAPI + '/wot/tanks/stats/'

    def __init__(self, accountId, config={}):
        self.__accountId = str(accountId)
        self.__vehicleList = PlayerVehicles(self.__accountId, config=config).list()
        super(PlayerVehicleStats, self).__init__(config=config)

    @property
    def cacheFile(self):
        return 'playervehiclestats_{}.json'.format(self.__accountId)

    @property
    def requestParam(self):
        fields = ( 'tank_id', 'random.battles', 'random.wins', 'random.spotted', 'random.frags',
                'random.damage_dealt', 'random.dropped_capture_points' )
        return {
            'application_id': APPLICATION_ID,
            'account_id': self.__accountId,
            'extra': 'random',
            'fields': ','.join(fields)
        }

    def fetch(self):
        self.cache = {}
        rest = self.__vehicleList
        while rest:
            if len(rest) > 100:
                curr, rest = rest[:100], rest[100:]
            else:
                curr, rest = rest, []
            param = self.requestParam
            param['tank_id'] = ','.join(map(str, curr))
            result = self.fetchJSON(self.sourceURL, param)
            for stats in result['data'][self.__accountId]:
                self.cache[str(stats['tank_id'])] = stats
        self.saveCache()

    def get(self, tankId):
        return self.cache[str(tankId)]

        
class PlayerList(CachedDatabase):
    cacheLifetime = 60 * 60 * 24 * 1
    cacheFile = 'playerlist.json'
    sourceURL = URL_WGAPI + '/wot/account/list/'

    @property
    def requestParam(self):
        return {
            'application_id': APPLICATION_ID,
            'search': self.__accountName,
            'type': 'exact'
        }

    def fetch(self):
        if self.cache is None:
            self.cache = {}

    def __fetchPlayer(self):
        result = self.fetchJSON(self.sourceURL, self.requestParam)
        if not result['data']:
            raise 'not found'
        data = result['data'][0]
        data['timestamp'] = int(time())
        self.cache[data['nickname']] = data
        if data['nickname'] != self.__accountName:
            self.cache[self.__accountName] = { 'alias': data['nickname'], 'timestamp': data['timestamp'] }
        self.saveCache()

    def __getFromCache(self, accountName):
        stat = self.cache.get(accountName, None)
        if stat and time() - stat['timestamp'] <= self.cacheLifetime:
            if 'alias' in stat:
                return self.__getFromCache(stat['alias'])
            return stat
        return None
    
    def get(self, accountName):
        if not self.config.get('force', False):
            stat = self.__getFromCache(accountName)
            if stat:
                return stat
        self.__accountName = accountName
        self.__fetchPlayer()
        stat = self.__getFromCache(accountName)
        return stat


class WN8Exp(CachedDatabase):
    cacheLifetime = 60 * 60 * 12
    cacheFile = 'wn8exp.json'
    sourceURL = 'https://static.modxvm.com/wn8-data-exp/json/wn8exp.json'

    def readCache(self):
        super(WN8Exp, self).readCache()
        self.__data = {}
        for row in self.cache['data']:
            self.__data[str(row['IDNum'])] = row

    def get(self, tankId):
        return self.__data[str(tankId)]

    def dump(self):
        return self.__data

    
if __name__ == '__main__':
    vehicleDatabase = VehicleDatabase()

    playerList = PlayerList()
    result = playerList.get('Chirimen')
    print result

    accountId = result['account_id']

    playerVehicleStats = PlayerVehicleStats(accountId)
    result = playerVehicleStats.dump()
    tank_id = result.keys()[0]
    print len(result)
    result = playerVehicleStats.get(tank_id)
    print result
    result = vehicleDatabase.get(tank_id)
    print result

    wn8Exp = WN8Exp()
    result = wn8Exp.get(tank_id)
    print result

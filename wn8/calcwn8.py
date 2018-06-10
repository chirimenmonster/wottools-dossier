# -*- coding: utf-8 -*- 

import sys
import codecs
import argparse
import wgapi
from wgapi import CachedDatabase

sys.stdout = codecs.getwriter('utf8')(sys.stdout)


def calcWN8(avg, exp):
    avgDmg, avgSpot, avgFrag, avgDef, avgWinRate = avg
    expDmg, expSpot, expFrag, expDef, expWinRate = exp

    # STEP1
    rDAMAGE = avgDmg     / expDmg
    rSPOT   = avgSpot    / expSpot
    rFRAG   = avgFrag    / expFrag
    rDEF    = avgDef     / expDef
    rWIN    = avgWinRate / expWinRate

    # STEP2
    rWINc    = max(0,                     (rWIN    - 0.71) / (1 - 0.71) )
    rDAMAGEc = max(0,                     (rDAMAGE - 0.22) / (1 - 0.22) )
    rFRAGc   = max(0, min(rDAMAGEc + 0.2, (rFRAG   - 0.12) / (1 - 0.12)))
    rSPOTc   = max(0, min(rDAMAGEc + 0.1, (rSPOT   - 0.38) / (1 - 0.38)))
    rDEFc    = max(0, min(rDAMAGEc + 0.1, (rDEF    - 0.10) / (1 - 0.10)))

    # STEP3():
    WN8 = 980 * rDAMAGEc + 210 * rDAMAGEc * rFRAGc + 155 * rFRAGc * rSPOTc + 75 * rDEFc * rFRAGc + 145 * min(1.8, rWINc)

    return WN8


class WN8Data(CachedDatabase):
    cacheLifetime = 60 * 60 * 24 * 1
    statsKeys = ( 'damage_dealt', 'spotted', 'frags', 'dropped_capture_points' )
    wn8ExpKeys = ( 'expDamage', 'expSpot', 'expFrag', 'expDef' )

    def __init__(self, accountId, config={}):
        self.__accountId = str(accountId)
        super(WN8Data, self).__init__(config=config)

    @property
    def cacheFile(self):
        return 'wn8data_{}.json'.format(self.__accountId)

    def fetch(self):
        self.vehicleDB = wgapi.VehicleDatabase(config=self.config)
        self.vehicleStats = wgapi.PlayerVehicleStats(self.__accountId, config=self.config)
        self.wn8Exp = wgapi.WN8Exp(config=self.config)
        self.cache = {}
        stats = { k: v['random'] for k, v in self.vehicleStats.items() }
        self.cache = {
            'player': { 'account_id': self.__accountId },
            'total': None,
            'vehicles': {}
        }
        for tankId in self.vehicleStats.keys():
            self._fetchVehicle(tankId)
        self._fetchTotal()
        self.saveCache()

    def _fetchVehicle(self, tankId):
        stats = self.vehicleStats.get(tankId)['random']
        wn8Exps = self.wn8Exp.get(tankId)
        battles = stats['battles']
        winRate = float(stats['wins']) / battles * 100
        avg = [ float(stats[k]) / battles for k in self.statsKeys ] + [ winRate ]
        exp = [ wn8Exps[k] for k in self.wn8ExpKeys + ( 'expWinRate', ) ]
        wn8 = calcWN8(avg, exp)
        result = self.cache['vehicles'][tankId] =  { 'battles': battles, 'wn8': wn8 }
        return result

    def _fetchTotal(self):
        totalStats = { k:0 for k in self.statsKeys + ( 'wins', 'battles' ) }
        totalWn8Exps = { k:0 for k in self.wn8ExpKeys + ( 'expWins', ) }
        for tankId in self.vehicleStats.keys():
            stats = self.vehicleStats.get(tankId)['random']
            wn8Exps = self.wn8Exp.get(tankId)
            battles = stats['battles']
            for key in totalStats.keys():
                totalStats[key] += stats[key]
            for key in self.wn8ExpKeys:
                totalWn8Exps[key] += wn8Exps[key] * battles
            totalWn8Exps['expWins'] += wn8Exps['expWinRate'] * battles / 100
        battles = totalStats['battles']
        winRate = float(totalStats['wins']) / battles * 100
        expWinRate = float(totalWn8Exps['expWins']) / battles * 100
        avg = [ float(totalStats[k]) / battles for k in self.statsKeys ] + [ winRate ]
        exp = [ totalWn8Exps[k] / battles for k in self.wn8ExpKeys ] + [ expWinRate ]
        wn8 = calcWN8(avg, exp)
        totalStats['battles'] = battles
        totalStats['wn8'] = wn8
        result = self.cache['total'] = totalStats
        return result

    def getVehicles(self):
        return self.cache['vehicles'].keys()

    def get(self, tankId):
        return self.cache['vehicles'][tankId]

    def getTotal(self):
        return self.cache['total']


def getWN8(nickname, config={}):
    accountId = wgapi.PlayerList(config=config).get(nickname)['account_id']
    wn8Data = WN8Data(accountId, config=config)
    result = wn8Data.dump()
    stats = wgapi.PlayerVehicleStats(accountId)
    for k, v in stats.items():
        result['vehicles'][k].update(v['random'])
    return result, wn8Data.lastmodified


def output(wn8Json):
    vehicleDB = wgapi.VehicleDatabase()

    order = {}
    order['tier'] = lambda x: - vehicleDB.getOrder(x, 'tier')
    order['type'] = lambda x: vehicleDB.getOrder(x, 'type')
    order['nation'] = lambda x: vehicleDB.getOrder(x, 'nation')

    template = u'{:>8}  {:^5} {:8} {:^6} {:24} {:>8} {:>6}'
    print template.format('id', 'tier', 'nation', 'type', 'name', 'battles', 'wn8')
    
    statsVehicles = wn8Json['vehicles']
    for tankId in sorted(statsVehicles.keys(), key=lambda x: [ order[k](x) for k in 'tier', 'type', 'nation' ]):
        stats = statsVehicles[tankId]
        vehicle = vehicleDB.get(tankId)
        tier = vehicle['tier'] if vehicle else ''
        type = vehicleDB.getType(tankId)
        name = vehicle['name'] if vehicle else ''
        if vehicle:
            nation = vehicle['nation']
        else:
            nation = wgapi.NATION_NAMES[int(tankId) >> 4 & 15]
        battles = stats['battles']
        wn8 = int(round(stats['wn8']))
        print template.format(tankId, tier, nation, type, name, battles, wn8)

    statsTotal = wn8Json['total']
    print template.format('', '', '', '', 'total', statsTotal['battles'], int(round(statsTotal['wn8'])))


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-p', dest='nickname', required=True, help='specify <WoT Account Name>')
    parser.add_argument('-f', dest='force', action='store_true', help='force to fetch, regaredless of the cache')
    
    config = parser.parse_args()

    options = { 'force': config.force }
    result, _ = getWN8(config.nickname, config=options)

    output(result)

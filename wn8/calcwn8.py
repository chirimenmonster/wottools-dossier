# -*- coding: utf-8 -*- 

import wgapi
import json

#with open('wn8exp.json', 'r') as fp:
#    wn8data = json.load(fp)
#    wn8DB = { str(v['IDNum']):v for v in wn8data['data'] }

#with open('vehiclestats.json', 'r') as fp:
#    stats = json.load(fp)


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


def getWN8(stats, expected):
    totalStats = { 'damage_dealt': 0, 'spotted': 0 , 'frags': 0, 'dropped_capture_points': 0, 'wins': 0, 'battles': 0 }
    totalExpected = { 'expDamage': 0, 'expSpot': 0, 'expFrag': 0, 'expDef': 0 , 'expWins': 0 }
    for tankId, value in stats.items():
        battles = value['battles']
        winRate = float(value['wins']) / battles * 100
        avg = [ float(value[k]) / battles for k in ('damage_dealt', 'spotted', 'frags', 'dropped_capture_points') ] + [ winRate ]
        exp = [ expected[tankId][k] for k in ('expDamage', 'expSpot', 'expFrag', 'expDef', 'expWinRate') ]
        stats[tankId]['wn8'] = calcWN8(avg, exp)
        for key in totalStats.keys():
            totalStats[key] += stats[tankId][key]
        for key in ('expDamage', 'expSpot', 'expFrag', 'expDef'):
            totalExpected[key] += expected[tankId][key] * battles
        totalExpected['expWins'] += expected[tankId]['expWinRate'] * battles / 100
    battles = totalStats['battles']
    winRate = float(totalStats['wins']) / battles * 100
    expWinRate = float(totalExpected['expWins']) / battles * 100
    avg = [ float(totalStats[k]) / battles for k in ('damage_dealt', 'spotted', 'frags', 'dropped_capture_points') ] + [ winRate ]
    exp = [ totalExpected[k] / battles for k in ('expDamage', 'expSpot', 'expFrag', 'expDef') ] + [ expWinRate ]
    wn8 = calcWN8(avg, exp)
    return battles, wn8


def main():
    vehicleDB = wgapi.VehicleDatabase()
    accountId = wgapi.PlayerList().get('Chirimen')['account_id']
    stats = wgapi.PlayerVehicleStats(accountId).dump()
    wn8DB = wgapi.WN8Exp().dump()

    data = { tankId: value['random'] for tankId, value in stats.items() }
    battles, wn8 = getWN8(data, wn8DB)

    for tankId in sorted(stats.keys(), key=lambda x: vehicleDB.get(x)['tier']):
        vehicle = vehicleDB.get(tankId)
        print '{:>6} {:2} {:>24} {:8} {:6}'.format(tankId, vehicle['tier'], vehicle['name'].encode('utf8'),
                stats.get(tankId)['random']['battles'], int(round(data[tankId]['wn8'])))
    print '{:6} {:2} {:>24} {:8} {:6}'.format('', '', 'total', battles, int(round(wn8)))

main()

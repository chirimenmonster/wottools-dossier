# -*- coding: utf-8 -*- 

import argparse
import wgapi


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


def getWN8(stats, wn8Exp):
    statsKeys = ( 'damage_dealt', 'spotted', 'frags', 'dropped_capture_points' )
    wn8ExpKeys = ( 'expDamage', 'expSpot', 'expFrag', 'expDef' )
    totalStats = { k:0 for k in statsKeys + ( 'wins', 'battles' ) }
    totalExpected = { k:0 for k in wn8ExpKeys + ( 'expWins', ) }
    
    for tankId in stats.keys():
        value = stats[tankId]
        expected = wn8Exp.get(tankId)
        battles = value['battles']
        winRate = float(value['wins']) / battles * 100
        avg = [ float(value[k]) / battles for k in statsKeys ] + [ winRate ]
        exp = [ expected[k] for k in wn8ExpKeys + ( 'expWinRate', ) ]

        value['wn8'] = calcWN8(avg, exp)

        for key in totalStats.keys():
            totalStats[key] += value[key]
        for key in wn8ExpKeys:
            totalExpected[key] += expected[key] * battles
        totalExpected['expWins'] += expected['expWinRate'] * battles / 100

    battles = totalStats['battles']
    winRate = float(totalStats['wins']) / battles * 100
    expWinRate = float(totalExpected['expWins']) / battles * 100
    avg = [ float(totalStats[k]) / battles for k in statsKeys ] + [ winRate ]
    exp = [ totalExpected[k] / battles for k in wn8ExpKeys ] + [ expWinRate ]
    wn8 = calcWN8(avg, exp)
    return battles, wn8


def main(config):
    vehicleDB = wgapi.VehicleDatabase()
    accountId = wgapi.PlayerList().get(config.nickname)['account_id']
    playerVehicleStats = wgapi.PlayerVehicleStats(accountId)
    wn8Exp = wgapi.WN8Exp()

    stats = { k: v['random'] for k, v in playerVehicleStats.items() }
    battles, wn8 = getWN8(stats, wn8Exp)

    order = {}
    order['tier'] = lambda x: - vehicleDB.getOrder(x, 'tier')
    order['type'] = lambda x: vehicleDB.getOrder(x, 'type')
    order['nation'] = lambda x: vehicleDB.getOrder(x, 'nation')

    template = u'{:>8}  {:^5} {:8} {:^6} {:24} {:>8} {:>6}'
    print template.format('id', 'tier', 'nation', 'type', 'name', 'battles', 'wn8')

    for tankId in sorted(stats.keys(), key=lambda x: [ order[k](x) for k in 'tier', 'type', 'nation' ]):
        vehicle = vehicleDB.get(tankId)
        type = vehicleDB.getType(tankId)
        print template.format(tankId, vehicle['tier'], vehicle['nation'], type, vehicle['name'],
                stats[tankId]['battles'], int(round(stats[tankId]['wn8'])))
    print template.format('', '', '', '', 'total', battles, int(round(wn8)))


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-p', dest='nickname', required=True, help='specify <WoT Account Name>')
    
    config = parser.parse_args()
    main(config)

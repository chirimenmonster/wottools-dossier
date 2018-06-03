import os
import urllib
import json

wgApiUrl = 'https://api.worldoftanks.asia'
applicationId = 'demo'
accountId = '2003019760'

def wgapiGetRequest(url, param):
    paramStr = urllib.urlencode(param)
    readObj = urllib.urlopen(url + '?' + paramStr)
    response = readObj.read()
    return json.loads(response)


def getPlayerVehicles():
    url = wgApiUrl + '/wot/account/tanks/'
    param = {
        'application_id': applicationId,
        'account_id': accountId,
        'fields': 'tank_id'
    }
    return wgapiGetRequest(url, param)

def getVehicleList():
    url = wgApiUrl + '/wot/encyclopedia/vehicles/'
    param = {
        'application_id': applicationId,
        'fields': 'tank_id,tag,name,nation,tier,type'
    }
    return wgapiGetRequest(url, param)

def getVehicleStats(tankList):
    url = wgApiUrl + '/wot/tanks/stats/'
    param = {
        'application_id': applicationId,
        'account_id': accountId,
        'tank_id': ','.join(map(str, tankList)),
        'extra': 'random',
        'fields': 'tank_id,random.battles,random.wins,random.spotted,random.frags,random.damage_dealt,random.dropped_capture_points'
    }
    return wgapiGetRequest(url, param)


def getAllVehicleStats(tankList):
    work = tankList[:]
    list = []
    while len(work) > 0:
        if len(work) > 100:
            curr = work[:100]
            work = work[100:]
        else:
            curr = work
            work = []
        result = getVehicleStats(curr)
        list.extend(result['data'][accountId])
    data = { str(s['tank_id']):s for s in list }
    return data

if os.path.exists('allvehicles.json'):
    with open('allvehicles.json', 'r') as fp:
        database = json.load(fp)
else:
    result = getVehicleList()
    database = result['data']
    with open('allvehicles.json', 'w') as fp:
        json.dump(database, fp)

result = getPlayerVehicles()
vehicleList = [ str(d['tank_id']) for d in result['data'][accountId] ]
allstats = getAllVehicleStats(vehicleList)

for tank_id in vehicleList:
    allstats[tank_id]['vehicle'] = database[tank_id]

print 'stats fouund: {}'.format(len(allstats))

#for stats in allstats.values():
#    print stats['vehicle']['tank_id'], stats['vehicle']['tag'], stats['vehicle']['name'], stats['random']['battles']

with open('vehiclestats.json', 'w') as fp:
    json.dump(allstats, fp)

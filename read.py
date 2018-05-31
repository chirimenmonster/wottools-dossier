import struct
import json
import cPickle as pickle
from pprint import pprint
from datetime import datetime

FILE = 'test.dat'

nations = { i:n for i,n in enumerate(('ussr', 'germany', 'usa', 'china', 'france', 'uk',
    'japan', 'czech', 'sweden', 'poland', 'italy')) }

attrs = { i:a for i,a in enumerate(('xp', 'battlesCount', 'wins', 'losses', 'survivedBattles',
    'frags', 'shots', 'directHits', 'spotted', 'damageDealt',
    'damageReceived', 'capturePoints', 'droppedCapturePoints',
    'xpBefore8_8', 'battlesCountBefore8_8', 'winAndSurvived',
    'frags8p', 'battlesCountBefore9_0')) }


with open('dossierdescr.json', 'r') as fp:
    dossierDescr = json.load(fp)
    dossierBlockIndexes = { int(i):v for i,v in dossierDescr['indexes'].items() }
    print dossierBlockIndexes

with open('vehiclelist.json', 'r') as fp:
    vehicleDict = { v[0]:v[3] for v in json.load(fp) }

with open(FILE, 'r') as fp:
    version, rawdata = pickle.load(fp)

result = []
for (_, tankID), (timestamp, dossier) in rawdata.items():
    vehicle = vehicleDict.get(tankID, None)
    if not vehicle:
        nation = nations[tankID >> 4 & 15]
        itemID = tankID >> 8 & 65535
        vehicle = '{}:({})'.format(nation, itemID)
    #print vehicle, datetime.fromtimestamp(timestamp)
    version = struct.unpack_from('<H', dossier)[0]
    size = offset = 2
    blocksize = []
    while size < len(dossier):
        blocksize.append(struct.unpack_from('<H', dossier, offset)[0])
        offset += 2
        size += 2 + blocksize[-1]
    bstr = ', '.join(map('{:4d}'.format, blocksize))
    descr = { 'vehicle': vehicle, 'update': timestamp, 'version': version,
        'blocksize': blocksize }
    if blocksize[0] > 0:
        data = struct.unpack_from('<IIIIIIIIIIIIIIIIII', dossier, offset)
        stats = { k: data[i] for i, k in attrs.items() }
        descr['random'] = stats
    else:
        descr['random'] = {}
    result.append(descr)

for r in sorted(result, key=lambda x: x['update']):
    list = filter(lambda x:x[1] > 0, zip(dossierBlockIndexes.values(), r['blocksize']))
    d = ','.join(map(lambda x:x[0], list))
    print '{:>40s}: lastupdate= {}, version= {:4}, battlesCount= {:4}, d={}'.format(r['vehicle'], datetime.fromtimestamp(r['update']), r['version'], r['random'].get('battlesCount', 0), d)

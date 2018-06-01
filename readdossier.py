import struct
import json
import cPickle as pickle
from pprint import pprint
from datetime import datetime

FILE = 'test.dat'

nations = { i:n for i,n in enumerate(('ussr', 'germany', 'usa', 'china', 'france', 'uk',
    'japan', 'czech', 'sweden', 'poland', 'italy')) }


with open('dossierdescr.json', 'r') as fp:
    dossierDescr = json.load(fp)
    DOSSIER_BLOCK_INDEXES = { v:int(i) for i,v in dossierDescr['indexes'].items() }
    DOSSIER_LAYOUTS = {}
    for d in dossierDescr['layout'].values():
        if d['class'] == 'StaticDossierBlockDescr':
            DOSSIER_LAYOUTS[d['name']] = {}
            DOSSIER_LAYOUTS[d['name']]['format'] = d['format']
            DOSSIER_LAYOUTS[d['name']]['recordsLayout'] = [ p[0] for p in d['recordsLayout'] ]

with open('blockslayout.json', 'r') as fp:
    DOSSIER_BLOCKS_LAYOUTS = json.load(fp)

with open('vehiclelist.json', 'r') as fp:
    VEHICLE_DICT = { v[0]:v for v in json.load(fp) }


def getVehicleName(compactDescr):
    info = VEHICLE_DICT.get(compactDescr, None)
    if info:
        name = info[3]
    else:
        nation = nations[compactDescr >> 4 & 15]
        itemId = compactDescr >> 8 & 65535
        name = '{}:({})'.format(nation, itemId)
    return name


def loadVehiclesDossier(file):
    with open(file, 'r') as fp:
        _, rawdata = pickle.load(fp)

    result = []
    for (_, ownerId), (timestamp, dossierCompDescr) in rawdata.items():
        vehicle = getVehicleName(ownerId)
        version = struct.unpack_from('<H', dossierCompDescr)[0]
        
        nBlocks = DOSSIER_BLOCKS_LAYOUTS[str(version)]['nBlocks']
        blockSize = struct.unpack_from('<{:d}H'.format(nBlocks), dossierCompDescr, 2)
        blockOffset = [0] * len(blockSize)
        for i in range(len(blockSize) - 1):
            blockOffset[i + 1] = blockOffset[i] + blockSize[i] 

        descr = { 'vehicle': vehicle, 'update': timestamp, 'version': version,
            'blockSize': blockSize, 'random': {} }

        baseOffset = 2 + nBlocks * 2
        if blockSize[DOSSIER_BLOCK_INDEXES['a15x15']] > 0:
            offset = baseOffset + blockOffset[DOSSIER_BLOCK_INDEXES['a15x15']]
            data = struct.unpack_from(DOSSIER_LAYOUTS['a15x15']['format'], dossierCompDescr, offset)
            stats = { k: data[i] for i, k in enumerate(DOSSIER_LAYOUTS['a15x15']['recordsLayout']) }
            descr['random'] = stats

        result.append(descr)
    return result


result = loadVehiclesDossier(FILE)

for r in sorted(result, key=lambda x: x['update']):
    #list = filter(lambda x:x[1] > 0, zip(dossierBlockIndexes.values(), r['blockSize']))
    #d = ','.join(map(lambda x:x[0], list))
    battlesCount = r['random'].get('battlesCount', None)
    if battlesCount:
        print '{:>40s}: update= {}, version= {:4}, random.battlesCount= {:4}'.format(r['vehicle'], datetime.fromtimestamp(r['update']), r['version'], battlesCount)

import struct
import json
import cPickle as pickle
from pprint import pprint

FILE = 'test.dat'

with open('vehiclelist.json', 'r') as fp:
    vehicleDict = { v[0]:v for v in json.load(fp) }

with open(FILE, 'r') as fp:
    version, rawdata = pickle.load(fp)


timestamp, dossier = rawdata[(2, 1)]

data = struct.unpack_from('<IIIIIIIIIIIIIIIIII', dossier, 70)
attrs = ('xp', 'battlesCount', 'wins', 'losses', 'survivedBattles',
    'frags', 'shots', 'directHits', 'spotted', 'damageDealt',
    'damageReceived', 'capturePoints', 'droppedCapturePoints',
    'xpBefore8_8', 'battlesCountBefore8_8', 'winAndSurvived',
    'frags8p', 'battlesCountBefore9_0')

index = {}
for i, k in enumerate(attrs):
    index[k] = i

print vehicleDict[1][3]
for k in attrs:
    print '{}: {}'.format(k, data[index[k]])

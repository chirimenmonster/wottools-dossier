from PlayerEvents import g_playerEvents

FILE_VEHICLELIST = 'mods/logs/vehiclelist.json'

def init():
    print 'mod getvehiclelist'
    g_playerEvents.onAccountBecomePlayer += handler

def handler():
    try:
        print 'mod getvehiclelist: getVehicleList()'
        getVehicleList()
    except:
        import traceback
        traceback.print_exc()

def makeDirs(file):
    import os
    try:
        os.makedirs(os.path.dirname(file))
    except:
        pass


def saveDataJSON(file, data):
    import json
    import codecs
    makeDirs(file)
    with codecs.open(file, 'w') as fp:
        json.dump(data, fp, sort_keys=True, indent=4, ensure_ascii=False, encoding='utf8', separators=(',', ':'))


def saveDataPickle(file, data):
    import cPickle as pickle
    makeDirs(file)
    with open(file, 'wb') as fp:
        pickle.dump(data, fp)


def getVehicleList():
    import nations
    from constants import VEHICLE_CLASSES
    from items.vehicles import g_list
    from helpers import getFullClientVersion
    data = {}
    for nationId in nations.INDICES.values():
        for v in g_list.getList(nationId).values():
            nation, tag = v.name.split(':')
            data[v.compactDescr] = {
                'name': v.userString,
                'nation': nation,
                'tag': tag,
                'tier': v.level,
                'type': VEHICLE_CLASSES[v.typeID],
                'tank_id': v.compactDescr
            }
    size = len(data)
    result = {
        'meta': {
            'count': size,
            'total': size,
            'version': getFullClientVersion()
        },
        'data': data }
    saveDataJSON(FILE_VEHICLELIST, result)

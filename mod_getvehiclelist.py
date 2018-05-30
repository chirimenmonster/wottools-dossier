from PlayerEvents import g_playerEvents

FILE_VEHICLELIST = 'mods/logs/vehiclelist.json'
FILE_DOSSIERDESCR = 'mods/logs/dossierdescr.json'

def init():
    print 'mod getvehiclelist'
    g_playerEvents.onAccountBecomePlayer += getVehicleList
    g_playerEvents.onAccountBecomePlayer += getVehicleDossierDescr


def makeDirs(file):
    import os
    try:
        os.makedirs(os.path.dirname(file))
    except:
        pass


def saveDataJSON(file, data):
    import json
    makeDirs(file)
    with open(file, 'wb') as fp:
        json.dump(data, fp, sort_keys=True, indent=4, separators=(',', ':'))


def saveDataPickle(file, data):
    import cPickle as pickle
    makeDirs(file)
    with open(file, 'wb') as fp:
        pickle.dump(data, fp)


def getVehicleList():
    import nations
    from items.vehicles import g_list
    rows = []
    for nationId in nations.INDICES.values():
        for v in g_list.getList(nationId).values():
            descr = ( v.compactDescr, nationId, v.id, v.name )
            rows.append(descr)
    rows = sorted(rows, key=lambda x: (x[1], x[2]))
    saveDataJSON(FILE_VEHICLELIST, rows)


def getVehicleDossierDescr():
    from dossiers2.custom import builders
    import dossiers2
    from pprint import pprint
    descr = builders.getVehicleDossierDescr()
    data = {}
    data['indexes'] = { v:k for k,v in descr._DossierDescr__blocksIndexes.items() }
    data['layout'] = {}
    for index in sorted(data['indexes'].keys()):
        key = data['indexes'][index]
        blockBuilder = descr[key]
        print index, key, type(blockBuilder)
        d = data['layout'][index] = { 'name': key }
        if isinstance(blockBuilder, dossiers2.common.DossierBlocks.StaticDossierBlockDescr):
            d['class'] = 'StaticDossierBlockDescr'
            d['blockSize'] = blockBuilder._StaticDossierBlockDescr__blockSize
            d['format'] = blockBuilder._StaticDossierBlockDescr__format
            d['recordsLayout'] = blockBuilder._StaticDossierBlockDescr__recordsLayout
        elif isinstance(blockBuilder, dossiers2.common.DossierBlocks.ListDossierBlockDescr):
            d['class'] = 'ListDossierBlockDescr'
            d['itemSize'] = blockBuilder._ListDossierBlockDescr__itemSize
            d['itemFormat'] = blockBuilder._ListDossierBlockDescr__itemFormat
        elif isinstance(blockBuilder, dossiers2.common.DossierBlocks.DictDossierBlockDescr):
            d['class'] = 'DictDossierBlockDescr'
            d['itemSize'] = blockBuilder._DictDossierBlockDescr__itemSize
            d['itemFormat'] = blockBuilder._DictDossierBlockDescr__itemFormat
        elif isinstance(blockBuilder, dossiers2.common.DossierBlocks.BinarySetDossierBlockDescr):
            d['class'] = 'BinarySetDossierBlockDescr'
        else:
            d['class'] = '{}'.format(type(blockBuilder))
            print 'unknwon: {}'.format(type(blockBuilder))
    pprint(data)
    saveDataJSON(FILE_DOSSIERDESCR, data)
